import requests
from rich import print
import json

import uvicorn
from thinking_neuron.models.request import ThinkingServerConfig
from thinking_neuron.thinking_server import ServerConfigRequest, ThinkingNeuronServer
from thinking_neuron.models import ModelSettings

HOST = "http://0.0.0.0:8000"
THINK_URL = f"{HOST}/think"
UPDATE_SETTINGS_URL = f"{HOST}/update_settings"
LIST_MODELS_URL = f"{HOST}/list_models"
DOCS_URL = f"{HOST}/openapi.json"
PULL_MODEL_URL = f"{HOST}/pull_model"


def test_think(server):
    response = requests.post(THINK_URL, json={"text": "What's up dude?"})
    data = response.json()
    stream_url = data["stream_url"]
    stream_url = f"{HOST}{stream_url}"

    response = requests.get(stream_url, stream=True)
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode(), end="", flush=True)
            assert isinstance(chunk.decode(), str)

    assert response.status_code == 200


def test_update_settings(server):
    model_settings = ModelSettings(model="gemma:7b")
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
    response = requests.post(PULL_MODEL_URL, json={"model": "gemma:7b"})
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

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode(), end="", flush=True)
            assert isinstance(chunk.decode(), str)

    assert response.status_code == 200


# stream_id = data["stream_url"]
# stream_url = f"{HOST}{stream_id}"

# response = requests.get(stream_url, stream=True)

# for chunk in response.iter_content(chunk_size=1024):
#     if chunk:
#         print(chunk.decode(), end="", flush=True)


# GET_LOGS_URL = f"{HOST}/logs"

# response = requests.get(GET_LOGS_URL)
# data = response.json()
# print(data)


# GET_CODE_FILES = f"{HOST}/code"

# response = requests.get(GET_CODE_FILES)
# data = response.json()

# print(data)
