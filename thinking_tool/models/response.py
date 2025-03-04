import logging
from dataclasses import dataclass, asdict
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from thinking_tool.models.request import ThinkingServerConfig


logger = logging.getLogger(__name__ + "." + __file__)


class ModelLoadingResponse(BaseModel):
    model: str | None
    stream_id: str | None


class UpdateConfigResponse(BaseModel):
    config: ThinkingServerConfig


class ThinkingResponse(BaseModel):
    text: str | None

    # TODO: Can add response info with another
    # url to stream the results
    # stream_url: str


class StreamResponse(BaseModel):
    stream_url: str | None


class OllamaErroResponse(JSONResponse):
    status_code = 500

    def __init__(self, error_msg: str):
        content = {"message": f"Unable to connect to llama service.\n{error_msg}"}
        super().__init__(content=content)


class OllamaNoDownloadedModelsResponse(JSONResponse):
    status_code = 404
    error_msg: str
    available_models: list[str]

    def __init__(self, error_msg: str, available_models: list[str]):
        self.error_msg = error_msg
        self.available_models = available_models
