from typing import Any, AsyncGenerator, Generator
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field
import ollama
import json
from thinking_tool.models import (
    ThinkingServerConfig,
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

        self.client = ollama.Client(
            host=self.config.model_settings.host_uri(),
            timeout=self.config.model_settings.timeout,
        )
        self.aclient = ollama.AsyncClient(
            host=self.config.model_settings.host_uri(),
            timeout=self.config.model_settings.timeout,
        )
        self.update(self.config)

        # WILO: I need to handle if the model is not available
        # it should be pulled and loop here until it finishes
        # with periodic messages to the user about it pulling.

    def ready(self) -> LLM_ManagerResponse:
        self.client.show(self.config.model_settings.model)
        response = LLM_ManagerResponse(message="ready")

        return response

    def status(self) -> dict:
        response = LLM_ManagerResponse(message="not ready")

        if not self.ready().message == "ready":
            return response

        status = ollama.ShowResponse = ollama.show(self.config.model_settings.model)
        response = status.model_dump() | {"message": "ready"}

        return response

    def local_models_available(self) -> LLM_ManagerResponse:
        model_dump = self.client.list().model_dump()["models"]
        # Convert datetime objects to strings
        models = [json.loads(json.dumps(model, default=str)) for model in model_dump]

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
        message = f"pulling model {model}"
        _ = self.client.pull(model, stream=True)
        return LLM_ManagerResponse(message=message)

    async def pull_status(
        self, model: str
    ) -> Generator[ollama.ListResponse, None, None]:
        return await self.aclient.pull(model, stream=True)

    def update(self, config: ThinkingServerConfig) -> LLM_ManagerResponse:
        response = self.client.list()
        available_models = response.models
        available_model_names = [model.model for model in available_models]

        if config.model_settings.model not in available_model_names:
            self.pull(config.model_settings.model)

        self.config = config
        return LLM_ManagerResponse(message="Model updated")

    async def generate(
        self, messages: list[str]
    ) -> AsyncGenerator[ollama.ChatResponse, None]:
        messages = [
            ollama.Message(role="user", content=message) for message in messages
        ]
        async for chunk in await self.aclient.chat(
            self.config.model_settings.model, messages, stream=True
        ):
            logger.info(type(chunk))
            yield chunk
