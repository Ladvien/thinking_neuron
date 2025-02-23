from typing import Callable
from pydantic import BaseModel, Field

from thinking_neuron.models.request import ThinkingRequest


class Stream(BaseModel):
    text: str
    stream_id: str
    request: ThinkingRequest
    method: Callable = None
    media_type: str = "text/plain"
