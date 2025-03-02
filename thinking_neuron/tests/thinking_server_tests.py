import requests
from rich import print
import json
import pytest
import logging
import uvicorn
import os

from thinking_neuron.models.request import ThinkingServerConfig
from thinking_neuron.thinking_server import (
    ServerConfigRequest,
    ThinkingNeuronServer,
    ToolConfig,
)
from thinking_neuron.models import ModelSettings

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


def test_think(server, downloaded_model):
    response = requests.post(THINK_URL, json={"messages": ["What's up dude?"]})
    data = response.json()
    print(data)
    stream_url = data["stream_url"]
    stream_url = f"{HOST}{stream_url}"

    response = requests.get(stream_url, stream=True)
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode(), end="", flush=True)
            assert isinstance(chunk.decode(), str)

    assert response.status_code == 200


def test_update_settings(server, downloaded_model):
    model_settings = ModelSettings(model=downloaded_model)
    server_config = ThinkingServerConfig(
        name="bob",
        model_settings=model_settings,
    )
    data = ServerConfigRequest(config=server_config).model_dump()
    result = requests.post(UPDATE_SETTINGS_URL, json=data)

    assert result.status_code == 200


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
