from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class BaseLLM_ManagerConfig(BaseModel):
    model: str = Field(default="deepseek-r1:8b")
    host: str = Field(default="localhost")
    port: int = Field(default=11434)
    timeout: int = Field(default=10)

    def host_uri(self) -> str:
        return f"{self.host}:{self.port}"


class BaseLLM_ManagerResponse(BaseModel):
    pass


class BaseLLM_Manager(BaseModel):
    config: BaseLLM_ManagerConfig

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Pydantic v2 syntax
