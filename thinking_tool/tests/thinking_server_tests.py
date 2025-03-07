import ollama
from rich import print
import logging
import os

from thinking_tool.models.request import PullModelRequest, ThinkingServerConfig
from thinking_tool.self_awareness import CodeFile
from thinking_tool.tests.conftest import MODEL_FOR_PULL_TEST
from thinking_tool.thinking_server import (
    ServerConfigRequest,
)
from thinking_tool.models import ThinkingRequest
from thinking_tool.thinking_client import ThinkingToolClient

from thinking_tool.models import OllamaSettings

logger = logging.getLogger(__name__ + "." + __file__)


def test_think(server, downloaded_model, client: ThinkingToolClient):
    response = client.think(ThinkingRequest(messages=["What's up dude?"]))
    for chat_response in response:
        print(chat_response, end="", flush=True)
        assert isinstance(chat_response, ollama.ChatResponse)


def test_update_settings(server, downloaded_model, client: ThinkingToolClient):
    model_settings = OllamaSettings(model=downloaded_model)
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


def test_list_models(server, client: ThinkingToolClient):
    models = client.list_models()
    assert isinstance(models, list)


def test_api_docs(server, client: ThinkingToolClient):
    docs = client.get_docs()
    logger.info(docs)
    assert "openapi" in docs
    assert "info" in docs


def test_pull_code(server, client: ThinkingToolClient):
    code_files = client.get_code()
    logger.info(code_files)
    assert isinstance(code_files, list)
    assert isinstance(code_files[0], CodeFile)


def test_pull_model(server, client: ThinkingToolClient):
    response = client.pull_model(PullModelRequest(model=MODEL_FOR_PULL_TEST))
    logger.info(response)
    for pull_progress in response:
        print(pull_progress, end="", flush=True)
        assert isinstance(pull_progress, ollama.ProgressResponse)

    os.system(f"ollama rm {MODEL_FOR_PULL_TEST}")
