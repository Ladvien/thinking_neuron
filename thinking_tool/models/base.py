from abc import ABC
from typing import Any
from pydantic import BaseModel, Field


class LLM_ManagerConfig(BaseModel, ABC):
    model: str = Field(default="deepseek-r1:8b")
    host: str = Field(default="localhost")
    port: int = Field(default=11434)
    timeout: int = Field(default=10)

    def host_uri(self) -> str:
        return f"{self.host}:{self.port}"


class LLM_ManagerResponse(BaseModel, ABC):
    pass
