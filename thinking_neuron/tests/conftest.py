import pytest
from rich import print
import logging
import os
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient
import uvicorn
import contextlib
import time
import threading


from thinking_neuron.thinking_server import ThinkingNeuronServer, ToolConfig


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

    speech_neuron = ThinkingNeuronServer()
    app.include_router(speech_neuron.router)

    config = uvicorn.Config(app, host=HOST, port=PORT, log_level="info")
    server = Server(config=config)

    with server.run_in_thread():
        yield server
