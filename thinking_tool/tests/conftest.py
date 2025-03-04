import pytest
from rich import print
from fastapi import FastAPI
import uvicorn
import contextlib
import time
import threading
import logging

from thinking_tool.models.request import PullModelRequest, ThinkingServerConfig
from thinking_tool.models.response import UpdateConfigResponse
from thinking_tool.thinking_server import (
    ServerConfigRequest,
    ThinkingToolServer,
)
from thinking_tool.thinking_client import ThinkingToolClient
from thinking_tool.models import ModelSettings


logger = logging.getLogger(__name__ + "." + __file__)

SERVER_LOG_LEVEL = "info"

MODEL_FOR_PULL_TEST = "reader-lm"
SMALL_MODEL_NAME = "qwen2.5:0.5b"


class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


@pytest.fixture(scope="session")
def server():
    HOST = "0.0.0.0"
    PORT = 8000

    app = FastAPI()

    thinking_tool = ThinkingToolServer()
    app.include_router(thinking_tool.router)

    config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level=SERVER_LOG_LEVEL,
    )
    server = Server(config=config)

    with server.run_in_thread():
        yield server


@pytest.fixture
def downloaded_model(server, client: ThinkingToolClient):
    # Pull the model
    pull_model_request = PullModelRequest(model=MODEL_FOR_PULL_TEST)
    response = client.pull_model(pull_model_request)
    logger.info(response)

    logger.info("Model downloaded")

    # Update the model settings
    model_settings = ModelSettings(model=SMALL_MODEL_NAME)
    server_config = ThinkingServerConfig(
        name="bob",
        model_settings=model_settings,
    )
    response = client.update_settings(
        ServerConfigRequest(
            config=server_config,
        ),
    )

    isinstance(response, UpdateConfigResponse)

    logger.info(response)
    logger.info(f"Model settings updated to use: '{SMALL_MODEL_NAME}'")

    return SMALL_MODEL_NAME


@pytest.fixture
def client():
    return ThinkingToolClient()
