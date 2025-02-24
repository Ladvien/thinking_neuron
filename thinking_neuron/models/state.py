from typing import Callable
from pydantic import BaseModel, Field

from thinking_neuron.models.request import ThinkingRequest


class Stream(BaseModel):
    stream_id: str
    request: dict
    method: Callable = None
    media_type: str = "text/plain"
