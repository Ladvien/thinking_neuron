from uuid import uuid4
from fastapi.responses import JSONResponse
from langchain_ollama import OllamaLLM
from pydantic import BaseModel
import ollama
from .models import (
    ThinkingServerConfig,
    ServerConfigRequest,
)

import logging

logger = logging.getLogger(__name__ + "." + __file__)


class LLM_ManagerResponse(BaseModel):
    message: str
    models: dict = None
    stream_id: str = None
    stream: ollama.ListResponse = None


class Stream:
    def __init__(self, message: str, stream_id: str, request: dict, method: callable):
        self.message = message
        self.stream_id = stream_id
        self.request = request
        self.method = method


class LLM_Manager:

    def __init__(self, config: ThinkingServerConfig = None) -> None:
        self.config = config if config else ThinkingServerConfig()
        try:
            self.update(ServerConfigRequest(config=self.config))
            logger.info("LLM Manager initialized")
        except Exception as e:
            logger.error(f"Error initializing LLM Manager: {e}")

        self.model = None
        self.stream = None

    def ready(self) -> LLM_ManagerResponse:
        response = LLM_ManagerResponse(message="not ready")
        try:
            ollama.show(self.config.model_settings.model)
            logger.info("Ollama is running")
            response = LLM_ManagerResponse(message="ready")
        except ConnectionError:
            logging.error("Ollama may not be running.")
        except ollama.ResponseError as e:
            logging.error(f"Ollama error: {e}")
        except Exception as e:
            logging.error(f"Unknown error: {e}")

        return response

    def status(self) -> dict:
        response = LLM_ManagerResponse(message="not ready")

        if not self.ready().message == "ready":
            logger.error("Attempting to get model status when not ready")
            return response

        try:
            status = ollama.ShowResponse = ollama.show(self.config.model_settings.model)
            response = status.model_dump() | {"message": "ready"}
            logger.info(f"Model status: {response}")
        except Exception as e:
            error_message = f"Error getting model status: {e}"
            logging.error(error_message)
            response = {"message": error_message}

        logger.info("Model status:")
        logger.info(response)
        return response

    def local_models_available(self) -> JSONResponse:
        response = LLM_ManagerResponse(message="not ready")

        if not self.ready().message == "ready":
            logger.error("Attempting to get local models when not ready")
        else:
            response = LLM_ManagerResponse(
                message="Local models available", models=ollama.list().model_dump()
            )
            logger.info("Local models available:")
            logger.info(response)

        return response

    # TODO: There is no way to check if a model is available to download
    # would need to use website data or wait until feature is
    # implemented in ollama
    # https://github.com/ollama/ollama/issues/8241
    # def remote_models_available(self) -> list[str]:
    #     return ollama.ps()

    def pull(self, model_name: str) -> ollama.ProgressResponse:
        response = LLM_ManagerResponse(message="not ready")
        stream_id = str(uuid4())

        try:
            # Kicks of the pull, but doesn't provide stream.
            _ = ollama.pull(model_name, stream=True)
            message = f"Pulling model {model_name}"
            logger.info(message)
            self.stream = Stream(
                message=message,
                stream_id=stream_id,
                request={"model": model_name, "stream": True},
                method=ollama.pull,
            )
            response.stream_id = stream_id
        except Exception as e:
            error_message = f"Error pulling model: {e}"
            logging.error(error_message)

        return response

    def pull_status(
        self, stream_id: str
    ) -> LLM_ManagerResponse | ollama.ProcessResponse:
        if not self.stream and self.stream.stream_id == stream_id:
            message = f"No stream available matching stream_id: {stream_id}"
            logger.error(message)
            return LLM_ManagerResponse(message=message)
        else:
            return self.stream.method(**self.stream.request)

    def update(self, config: ThinkingServerConfig) -> dict:
        self.model = OllamaLLM(
            **self.config.model_settings.model_dump(),
        )
