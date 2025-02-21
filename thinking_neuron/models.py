from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field


class ModelSettings(BaseModel):
    model: str = Field(default="deepseek-r1:14b")


class ThinkingServerConfig(BaseModel):
    name: str = Field(default="deep_thought")
    model_settings: ModelSettings = ModelSettings()


class ServerConfigRequest(ThinkingServerConfig):
    pass


class UpdateConfigResponse(BaseModel):
    model: str


class ThinkingRequest(BaseModel):
    text: str | None


class ThinkingResponse(BaseModel):
    text: str | None

    # TODO: Can add response info with another
    # url to stream the results
    # stream_url: str
