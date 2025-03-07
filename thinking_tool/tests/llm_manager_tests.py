import pytest
from rich import print
from fastapi import FastAPI
import uvicorn
import contextlib
import time
import threading
import logging


from thinking_tool.llm_manager import LLM_Manager, LLM_ManagerResponse
from thinking_tool.models import ThinkingServerConfig, ServerConfigRequest
from thinking_tool.models.request import OllamaSettings

SERVER_LOG_LEVEL = "info"

MODEL_FOR_PULL_TEST = "reader-lm"
SMALL_MODEL_NAME = "qwen2.5:0.5b"
OLLAMA_HOST = "http://192.168.1.177"
OLLAMA_PORT = 11434


@pytest.fixture
def config():
    model_settings = OllamaSettings(
        model=MODEL_FOR_PULL_TEST,
        host=OLLAMA_HOST,
        port=OLLAMA_PORT,
    )
    server_config = ThinkingServerConfig(
        name="bob",
        model_settings=model_settings,
    )


def test_init_llm_manager(config):
    manager = LLM_Manager(config=config)
    assert manager.config == config
    assert manager.client.host == f"{OLLAMA_HOST}:{OLLAMA_PORT}"
    assert manager.aclient.host == f"{OLLAMA_HOST}:{OLLAMA_PORT}"
    assert manager.model is None
