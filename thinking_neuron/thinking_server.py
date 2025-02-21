import io
from typing import Any, Union
from fastapi import FastAPI, APIRouter
from langchain_ollama import ChatOllama
import yaml
from fastapi.responses import StreamingResponse
from uuid import uuid4
import os
import requests
from datetime import datetime
import re
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from typing import AsyncGenerator


from .response import ThinkingResponse
from .config import ThinkerConfig


class ThinkRequest(BaseModel):
    text: str


class ThinkingNeuronServer:

    def __init__(self, config: ThinkerConfig) -> None:
        self.config = config
        self.router = APIRouter()
        self.model = OllamaLLM(**self.config.model_settings.model_dump())

        self.router.add_api_route(
            "/think",
            self.think,
            methods=["POST"],
            response_class=StreamingResponse,
        )

    async def generate_response(
        self, request: ThinkRequest
    ) -> AsyncGenerator[str, None]:
        """Streams the response from the model"""
        template = """{question}"""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.model

        async for chunk in chain.astream({"question": request.text}):
            yield chunk  # Send each chunk of response as it arrives

    async def think(self, request: ThinkRequest) -> StreamingResponse:
        return StreamingResponse(
            self.generate_response(request), media_type="text/plain"
        )
