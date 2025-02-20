from pydantic import BaseModel


class ThinkingResponse(BaseModel):
    text: str | None
