import logging
from dataclasses import dataclass, asdict
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__ + "." + __file__)


class ModelSettings(BaseModel):
    model: str = Field(default="deepseek-r1")


class ThinkingServerConfig(BaseModel):
    name: str = Field(default="deep_thought")
    model_settings: ModelSettings = ModelSettings()


class ServerConfigRequest(BaseModel):
    config: ThinkingServerConfig


class ThinkingRequest(BaseModel):
    messages: list[str] | None


class PullModelRequest(BaseModel):
    model: str | None


class StreamResultRequest(BaseModel):
    stream_id: str | None


class PullModelRequest(BaseModel):
    model: str | None
