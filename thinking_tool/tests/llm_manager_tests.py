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
async def test_llm_manager_status_is_ready(config, ollama_client):
    try:
        await ollama_client.delete(SMALL_MODEL_NAME)
    except ollama._types.ResponseError as e:
        print("Didn't need to delete model")

    manager = LLM_Manager(config=config)
    await manager.status() == LLM_ManagerStatus.model_not_loaded
