import pytest
from rich import print
from fastapi import FastAPI
import uvicorn
import contextlib
import time
import threading
import logging
import ollama

from thinking_tool.llm_manager import (
    LLM_Manager,
    LLM_ManagerResponse,
    LLM_ManagerStatus,
)
from thinking_tool.models import ThinkingServerConfig, ServerConfigRequest
from thinking_tool.models.request import OllamaConfig

logger = logging.getLogger(__name__ + "." + __file__)

SERVER_LOG_LEVEL = "info"

MODEL_FOR_PULL_TEST = "reader-lm"
UNPULLED_MODEL_NAME = "qwen2.5:0.5b"
SMALL_MODEL_NAME = "qwen2.5:0.5b"
OLLAMA_HOST = "http://192.168.1.177"
OLLAMA_PORT = 11434


@pytest.fixture
def config():
    return OllamaConfig(
        model=MODEL_FOR_PULL_TEST,
        host=OLLAMA_HOST,
        port=OLLAMA_PORT,
    )


@pytest.fixture
def pulled_model(ollama_client):
    try:
        for chunk in ollama_client.pull(SMALL_MODEL_NAME):
            print(chunk)

    except ollama._types.ResponseError as e:
        print("Didn't need to pull model")

    yield SMALL_MODEL_NAME

    try:
        for chunk in ollama.delete(SMALL_MODEL_NAME):
            print(chunk)
    except ollama._types.ResponseError as e:
        print("Didn't need to delete model")


"""
LLM_Manager Design notes:
1. The LLM_Manager class is a wrapper around the Ollama AsyncClient class.
2. Its purpose is to abstract away the LLM details for the ThinkingServerTool.
3. It is async.

"""


@pytest.fixture
def ollama_client():
    return ollama.Client(f"{OLLAMA_HOST}:{OLLAMA_PORT}")


@pytest.mark.asyncio
async def test_init_llm_manager(config):
    manager = LLM_Manager(config=config)
    assert manager.config == config
    assert manager.client._client.base_url == f"{OLLAMA_HOST}:{OLLAMA_PORT}"
    assert manager.model is None


@pytest.mark.asyncio
async def test_llm_manager_status_returns_model_not_loaded_when_model_has_not_been_pulled(
    config,
    ollama_client,
):
    try:
        for chunk in ollama_client.delete(UNPULLED_MODEL_NAME):
            print(chunk)
    except ollama._types.ResponseError as e:
        print("Didn't need to delete model")

    manager = LLM_Manager(config=config)
    await manager.status() == LLM_ManagerStatus.model_not_loaded


@pytest.mark.asyncio
async def test_llm_manager_status_returns_ready_when_model_has_been_pulled(
    config,
    ollama_client,
    pulled_model,
):
    config.model = pulled_model
    manager = LLM_Manager(config=config)
    await manager.status() == LLM_ManagerStatus.ready


@pytest.mark.asyncio
async def test_llm_manager_load_returns_in_progress_status(
    config,
    ollama_client,
    pulled_model,
):
    config.model = pulled_model
    manager = LLM_Manager(config=config)
    await manager.status() == LLM_ManagerStatus.model_loading


@pytest.mark.asyncio
async def test_llm_manager_load_pulls_ollama_model(
    config,
    ollama_client,
    pulled_model,
):
    config.model = pulled_model
    manager = LLM_Manager(config=config)
    result = await manager.load(config.model)
    assert result.status == LLM_ManagerStatus.ready
    assert result.details["modelinfo"]["general.architecture"] == "qwen2"
    assert manager.config.model == config.model
