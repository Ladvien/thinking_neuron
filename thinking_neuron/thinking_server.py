import io
from typing import Any, Union
from fastapi import FastAPI, APIRouter
from langchain_ollama import ChatOllama
import yaml
from fastapi.responses import JSONResponse, StreamingResponse
from uuid import uuid4
import os
import requests
from datetime import datetime
import re
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from typing import AsyncGenerator

from .models import (
    ModelSettings,
    ThinkingServerConfig,
    ServerConfigRequest,
    UpdateConfigResponse,
    ThinkingRequest,
    ThinkingResponse,
)


class ThinkingNeuronServer:

    def __init__(self, config: ThinkingServerConfig = None) -> None:
        if config:
            self.config = config
        else:
            self.config = ThinkingServerConfig()

        self.router = APIRouter()
        self.model = OllamaLLM(
            **self.config.model_settings.model_dump(),
        )

        self.router.add_api_route(
            "/think",
            self.think,
            methods=["POST"],
            response_class=StreamingResponse,
        )

        self.router.add_api_route(
            "/update_settings",
            self.update_settings,
            methods=["POST"],
            response_class=StreamingResponse,
        )

    async def update_settings(
        self, request: ServerConfigRequest
    ) -> UpdateConfigResponse:
        data = UpdateConfigResponse(
            model=request.model_settings.model,
        )
        return JSONResponse(**data.model_dump())

    async def generate_response(
        self, request: ThinkingRequest
    ) -> AsyncGenerator[str, None]:
        """Streams the response from the model"""
        template = """{question}"""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.model

        async for chunk in chain.astream({"question": request.text}):
            yield chunk  # Send each chunk of response as it arrives

    async def think(self, request: ThinkingRequest) -> StreamingResponse:
        return StreamingResponse(
            self.generate_response(request), media_type="text/plain"
        )
