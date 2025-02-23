from dataclasses import dataclass, asdict
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ModelSettings(BaseModel):
    model: str = Field(default="deepseek-r1:14b")


class ThinkingServerConfig(BaseModel):
    name: str = Field(default="deep_thought")
    model_settings: ModelSettings = ModelSettings()


class ServerConfigRequest(ThinkingServerConfig):
    pass


class ThinkingRequest(BaseModel):
    text: str | None


class StreamResultRequest(BaseModel):
    stream_id: str | None
