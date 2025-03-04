from typing import Any, AsyncGenerator, Generator
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
        except ollama._types.ResponseError as e:
            message = f"Error initializing LLM Manager: {e}"
            logger.error(message)
            logger.info("Attempting to pull model")
            self.pull(self.config.model_settings.model)
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
            logger.error("Ollama may not be running.")
        except ollama.ResponseError as e:
            logger.error(f"Ollama error: {e}")
        except Exception as e:
            logger.error(f"Unknown error: {e}")

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
            logger.error(error_message)
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

        try:
            # TODO: Check if the model has already been downloaded.

            # Kicks of the pull, but doesn't provide stream.
            logger.info(f"Started pulling model: '{model}'")
            message = f"pulling model {model}"
            logger.info(message)

            _ = ollama.pull(model, stream=True)

            logger.info(f"Pulling model: '{model}'")

            return LLM_ManagerResponse(message=message)

        except ollama.ResponseError as e:
            error_message = f"Error pulling model: {e}"
            logger.error(error_message)
            return LLM_ManagerResponse(message=error_message)

        except Exception as e:
            error_message = f"Error pulling model: {e}"
            logger.error(error_message)
            return LLM_ManagerResponse(message=error_message)

    async def pull_status(
        self, model: str
    ) -> Generator[ollama.ListResponse, None, None]:
        return await ollama.AsyncClient().pull(model, stream=True)

    def update(self, config: ThinkingServerConfig) -> LLM_ManagerResponse:
        self.config = config
        logger.info("Config updated")
        return LLM_ManagerResponse(message="Model updated")

    async def generate(
        self, messages: list[str]
    ) -> AsyncGenerator[ollama.ChatResponse, None]:
        messages = [
            ollama.Message(role="user", content=message) for message in messages
        ]
        async for chunk in await ollama.AsyncClient().chat(
            self.config.model_settings.model, messages, stream=True
        ):
            logger.info(type(chunk))
            yield chunk
