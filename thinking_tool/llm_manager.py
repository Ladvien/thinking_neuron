from enum import Enum
from typing import Any, AsyncGenerator, Generator
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field
import ollama
import json

import logging

from thinking_tool.models.base import LLM_ManagerConfig


logger = logging.getLogger(__name__ + "." + __file__)


class LLM_ManagerStatus(Enum):
    ready = "ready"
    model_not_loaded = "model_not_loaded"
    error = "error"
    initializing = "initializing"
    unknown = "unknown"


class LLM_ManagerResponse(BaseModel):
    status: LLM_ManagerStatus = LLM_ManagerStatus.unknown
    models: Any = None
    stream_id: str = None
    stream: ollama.ListResponse = None


class LLM_Manager:

    model: Any = None

    def __init__(self, config: LLM_ManagerConfig = None) -> None:
        self.config = config if config else LLM_ManagerConfig()
        self.client = ollama.AsyncClient(
            host=self.config.host_uri(),
            timeout=self.config.timeout,
        )

    async def load(self, model: str) -> LLM_ManagerResponse:
        try:
            await self.client.pull(model)
            return LLM_ManagerResponse(status=LLM_ManagerStatus.ready)
        except ollama._types.ResponseError as e:
            return self._ollama_error_to_response(e)

    async def status(self) -> LLM_ManagerResponse:
        try:
            _ = await self.client.ps()
            return LLM_ManagerResponse(status=LLM_ManagerStatus.ready)
        except ollama._types.ResponseError as e:
            return self._ollama_error_to_response(e)

    # async def generate(
    #     self, messages: list[str]
    # ) -> AsyncGenerator[ollama.ChatResponse, None]:
    #     messages = [
    #         ollama.Message(role="user", content=message) for message in messages
    #     ]
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
