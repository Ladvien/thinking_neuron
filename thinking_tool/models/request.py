import logging
from typing import Callable
from pydantic import BaseModel, Field

from thinking_tool.models.config import OllamaConfig


logger = logging.getLogger(__name__ + "." + __file__)


class ThinkingServerConfig(BaseModel):
    name: str = Field(default="deep_thought")
    model_settings: OllamaConfig = OllamaConfig()


class ServerConfigRequest(BaseModel):
    config: ThinkingServerConfig


class ThinkingRequest(BaseModel):
    messages: list[str] | None


class PullModelRequest(BaseModel):
    model: str | None


class StreamResultRequest(BaseModel):
    stream_id: str | None


class StreamRequest(BaseModel):
    stream_id: str
    request: dict
    method: Callable = None
    media_type: str = "text/plain"
