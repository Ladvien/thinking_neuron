from pydantic import BaseModel, Field


class OllamaSettings(BaseModel):
    model: str = Field(default="deepseek-r1:8b")
    host: str = Field(default="localhost")
    port: int = Field(default=11434)
    timeout: int = Field(default=10)

    def host_uri(self) -> str:
        return f"{self.host}:{self.port}"
