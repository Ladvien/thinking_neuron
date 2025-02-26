from typing import Any
from uuid import uuid4
from fastapi.responses import JSONResponse
from langchain_ollama import OllamaLLM
from pydantic import BaseModel
import ollama
import json
from .models import (
    ThinkingServerConfig,
    ServerConfigRequest,
)

import logging

logger = logging.getLogger(__name__ + "." + __file__)


class LLM_ManagerResponse(BaseModel):
    message: str
    models: Any = None
    stream_id: str = None
    stream: ollama.ListResponse = None


class LLM_Manager:

    model: OllamaLLM = None

    def __init__(self, config: ThinkingServerConfig = None) -> None:
        self.config = config if config else ThinkingServerConfig()
        try:
            self.update(ServerConfigRequest(config=self.config))
            logger.info("LLM Manager initialized")
        except Exception as e:
            message = f"Error initializing LLM Manager: {e}"
            logger.error(message)
            raise Exception(message)

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

    def local_models_available(self) -> LLM_ManagerResponse:
        if not self.ready().message == "ready":
            logger.error("Attempting to get local models when not ready")
            return LLM_ManagerResponse(message="not ready")
        else:
            model_dump = ollama.list().model_dump()["models"]

            # Convert datetime objects to strings
            models = [
                json.loads(json.dumps(model, default=str)) for model in model_dump
            ]
            response = LLM_ManagerResponse(
                message="Local models available",
                models=models,
            )
            return response

    # TODO: There is no way to check if a model is available to download
    # would need to use website data or wait until feature is
    # implemented in ollama
    # https://github.com/ollama/ollama/issues/8241
    # def remote_models_available(self) -> list[str]:
    #     return ollama.ps()

    def pull(self, model: str) -> LLM_ManagerResponse:
        response = LLM_ManagerResponse(message="not ready")

        try:
            # Kicks of the pull, but doesn't provide stream.
            _ = ollama.pull(model, stream=True)
            message = f"Pulling model {model}"
            logger.info(message)
        except Exception as e:
            error_message = f"Error pulling model: {e}"
            logging.error(error_message)

        return response

    async def pull_stream(self, model: str) -> ollama.ProgressResponse:
        async for part ollama.AsyncClient().pull(model, stream=True):
            yield part

            

    def pull_status(
        self, stream_id: str
    ) -> LLM_ManagerResponse | ollama.ProcessResponse:
        if not self.stream and self.stream.stream_id == stream_id:
            message = f"No stream available matching stream_id: {stream_id}"
            logger.error(message)
            return LLM_ManagerResponse(message=message)
        else:
            return self.stream.method(**self.stream.request)

    def update(self, request: ServerConfigRequest) -> LLM_ManagerResponse:
        self.config = request.config
        model_settings_dump = self.config.model_settings.model_dump()

        self.model = OllamaLLM(**model_settings_dump)
        logger.info("Model updated")

        response = LLM_ManagerResponse(
            message="Model updated", models=model_settings_dump
        )

        logger.info(response)

        return response
