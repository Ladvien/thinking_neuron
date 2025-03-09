from enum import Enum
from typing import Any, Generator
from pydantic import BaseModel
import ollama

import logging

from thinking_tool.base import BaseLLM_Manager
from thinking_tool.models.config import OllamaConfig

logger = logging.getLogger(__name__ + "." + __file__)


Message = ollama.Message
ChatResponse = ollama.ChatResponse


class LLM_ManagerStatus(Enum):
    ready = "ready"
    model_loading = "model_loading"
    model_not_loaded = "model_not_loaded"
    generating = "generating"
    error = "error"
    initializing = "initializing"
    unknown = "unknown"


class LLM_ManagerResponse(BaseModel):
    status: LLM_ManagerStatus = LLM_ManagerStatus.unknown
    models: Any = None
    details: dict = None
    stream: Any = None


class OllamaLLM_Manager(BaseLLM_Manager):

    config: OllamaConfig
    _client: ollama.AsyncClient

    def __init__(
        self,
        config: OllamaConfig = None,
        **data,
    ) -> None:
        super().__init__(config=config, **data)
        self.config = config if config else OllamaConfig()
        self._client = ollama.AsyncClient(
            host=self.config.host_uri(),
            timeout=self.config.timeout,
        )

    async def load(self, model: str) -> Generator[ollama.ChatResponse, None, None]:
        available_models = await self._client.list()
        available_model_names = [model.model for model in available_models.models]

        if model not in available_model_names:
            return LLM_ManagerResponse(
                status=LLM_ManagerStatus.model_not_loaded,
                models=available_model_names,
            )

        self.config.model = model
        model_details = await self._client.show(model)

        try:
            return LLM_ManagerResponse(
                status=LLM_ManagerStatus.ready,
                models=model,
                details=model_details.model_dump(),
            )
        except ollama._types.ResponseError as e:
            return self._ollama_error_to_response(e)

    async def status(self) -> LLM_ManagerResponse:
        try:
            _ = await self._client.ps()
            return LLM_ManagerResponse(status=LLM_ManagerStatus.ready)
        except ollama._types.ResponseError as e:
            return self._ollama_error_to_response(e)

    async def chat(self, messages: list[Message]) -> LLM_ManagerResponse:
        try:
            model = await self._client.chat(
                model=self.config.model,
                messages=messages,
                stream=True,
                format="json",
            )
            return LLM_ManagerResponse(
                status=LLM_ManagerStatus.generating,
                stream=model,
            )
        except ollama._types.ResponseError as e:
            return self._ollama_error_to_response(e)

    # async def generate(
    #     self,
    #     messages: list[str],
    # ) -> AsyncGenerator[ollama.ChatResponse, None]:
    #     async for chunk in await self.client.chat(
    #         self.config.model_settings.model, messages, stream=True
    #     ):
    #         logger.info(type(chunk))
    #         yield chunk

    def _ollama_error_to_response(
        self, e: ollama._types.ResponseError
    ) -> LLM_ManagerResponse:
        logger.error(e)
        response = LLM_ManagerResponse(status=LLM_ManagerStatus.error)
        response.error = e
        return response
