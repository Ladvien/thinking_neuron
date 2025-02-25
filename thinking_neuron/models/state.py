import logging
from typing import Callable
from pydantic import BaseModel, Field

from thinking_neuron.models.request import ThinkingRequest

logger = logging.getLogger(__name__ + "." + __file__)


class Stream(BaseModel):
    stream_id: str
    request: dict
    method: Callable = None
    media_type: str = "text/plain"
