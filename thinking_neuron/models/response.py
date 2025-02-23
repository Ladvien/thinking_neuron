from dataclasses import dataclass, asdict
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class UpdateConfigResponse(BaseModel):
    model: str


class ThinkingResponse(BaseModel):
    text: str | None

    # TODO: Can add response info with another
    # url to stream the results
    # stream_url: str


class OllamaErroResponse(JSONResponse):
    status_code = 500

    def __init__(self, error_msg: str):
        content = {"message": f"Unable to connect to llama service.\n{error_msg}"}
        super().__init__(content=content)
