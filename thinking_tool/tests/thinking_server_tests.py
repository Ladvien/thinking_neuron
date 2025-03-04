import ollama
import requests
from rich import print
import json
import pytest
import logging
import uvicorn
import os

from thinking_tool.models.request import ThinkingServerConfig
from thinking_tool.models.response import StreamResponse
from thinking_tool.thinking_server import (
    ServerConfigRequest,
    ThinkingToolServer,
    ToolConfig,
)
from thinking_tool.models import ThinkingRequest
from thinking_tool.thinking_client import ThinkingToolClient

from thinking_tool.models import ModelSettings

HOST = "http://0.0.0.0:8000"
THINK_URL = f"{HOST}/think"
UPDATE_SETTINGS_URL = f"{HOST}/update_settings"
LIST_MODELS_URL = f"{HOST}/list_models"
DOCS_URL = f"{HOST}/openapi.json"
PULL_MODEL_URL = f"{HOST}/pull_model"
LOGS_URL = f"{HOST}/logs"
CODE_URL = f"{HOST}/code"

logger = logging.getLogger(__name__ + "." + __file__)

MODEL_FOR_PULL_TEST = "reader-lm"
SMALL_MODEL_NAME = "qwen2.5:0.5b"


@pytest.fixture
def downloaded_model(server):

    response = requests.post(
        PULL_MODEL_URL,
        json={"model": SMALL_MODEL_NAME},
    )
    data = response.json()

    logger.info(data)

    stream_id = data["stream_url"]
    stream_url = f"{HOST}{stream_id}"

    response = requests.get(stream_url, stream=True)

    assert response.status_code == 200

    logger.info("Starting download")

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode(), end="", flush=True)
            assert isinstance(chunk.decode(), str)

    logger.info("Model downloaded")

    # Update the model settings
    model_settings = ModelSettings(model=SMALL_MODEL_NAME)
    server_config = ThinkingServerConfig(
        name="bob",
        model_settings=model_settings,
    )
    data = ServerConfigRequest(config=server_config).model_dump()
    response = requests.post(UPDATE_SETTINGS_URL, json=data)

    logger.info(response.json())

    assert response.status_code == 200

    logger.info(f"Model settings updated to use: '{SMALL_MODEL_NAME}'")

    return SMALL_MODEL_NAME


@pytest.fixture
def client():
    return ThinkingToolClient(base_url=HOST)


def test_think(server, downloaded_model, client: ThinkingToolClient):
    response = client.think(ThinkingRequest(messages=["What's up dude?"]))
    for chat_response in response:
        print(chat_response, end="", flush=True)
        assert isinstance(chat_response, ollama.ChatResponse)


def test_update_settings(server, downloaded_model, client: ThinkingToolClient):
    model_settings = ModelSettings(model=downloaded_model)
    server_config = ThinkingServerConfig(
        name="test bob",
        model_settings=model_settings,
    )
    updated_config = client.update_settings(
        ServerConfigRequest(
            config=server_config,
        ),
    )

    logger.info(updated_config)

    assert updated_config.config.name == "test bob"
    assert updated_config.config.model_settings.model == downloaded_model


def test_list_models(server):
    result = requests.get(LIST_MODELS_URL)
    data = result.json()
    assert isinstance(data, list)
    assert result.status_code == 200


def test_api_docs(server):
    result = requests.get(DOCS_URL)
    docs_dict = result.json()
    assert isinstance(docs_dict, dict)
    assert result.status_code == 200


def test_pull_model(server):
    response = requests.post(PULL_MODEL_URL, json={"model": MODEL_FOR_PULL_TEST})
    data = response.json()
    print(data)

    stream_id = data["stream_url"]
    stream_url = f"{HOST}{stream_id}"

    response = requests.get(stream_url, stream=True)

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode(), end="", flush=True)
            assert isinstance(chunk.decode(), str)

    assert response.status_code == 200

    os.system(f"ollama rm {MODEL_FOR_PULL_TEST}")
