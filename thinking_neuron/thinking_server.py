from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from typing import AsyncGenerator
from uuid import uuid4
import ollama

from thinking_neuron.llm_manager import LLM_Manager
from thinking_neuron.models.request import PullModelRequest, StreamResultRequest
from thinking_neuron.models.response import OllamaPullModelStreamResponse
from thinking_neuron.models.state import Stream

from .models import ThinkingResponse, OllamaErroResponse, UpdateConfigResponse
from .models import (
    ThinkingServerConfig,
    ServerConfigRequest,
    ThinkingRequest,
)


class ThinkingNeuronServer:

    def __init__(self) -> None:

        self.last_response_stream = None

        self.llm_mang = LLM_Manager()

        self.router = APIRouter()

        self.router.add_api_route(
            "/list_models",
            self.list_models,
            methods=["GET"],
            response_class=JSONResponse,
        )

        self.router.add_api_route(
            "/pull_model",
            self.pull_model,
            methods=["POST"],
            response_class=JSONResponse,
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
            response_class=JSONResponse,
        )

        self.router.add_api_route(
            "/stream_response",
            self.stream_response,
            methods=["GET"],
            response_class=StreamingResponse,
        )

    async def list_models(self) -> JSONResponse:
        """
        Lists all available models

        Returns:
            JSONResponse: A response containing the list
        """
        models = ollama.list().model_dump_json()
        return JSONResponse(models)

    async def pull_model(self, request: PullModelRequest) -> JSONResponse:
        """
        Pulls a model from the ollama service

        Args:
            model (str): The model to pull

        Returns:
            JSONResponse: The response of the pull
        """
        self.last_response_stream = Stream(
            stream_id=str(uuid4()),
            request={"model": request.model, "stream": True},
            # WILO: The `ProgressResponse` does not work with the existing
            # streaming response I've implemented.  I'll need to refactor
            method=ollama.pull,
        )

        return JSONResponse(
            {
                "text": f"Attempting to download model: '{request.model}'",
                "stream_url": f"/stream_response?stream_id={self.last_response_stream.stream_id}",
            }
        )

    async def update_settings(
        self, request: ServerConfigRequest
    ) -> UpdateConfigResponse:
        """
        Updates the settings of the server

        Args:
            request (ServerConfigRequest): The request to update the settings

        Returns:
            UpdateConfigResponse: The updated settings
        """
        response = self.llm_mang.update_settings(request)
        return response

    async def think(self, request: ThinkingRequest) -> StreamingResponse:
        """
        Thinks about the question

        Args:
            request (ThinkingRequest): The request to think about

        Returns:
            JSONResponse: The response to the question
        """
        stream_id = str(uuid4())
        self.last_response_stream = Stream(
            text=request.text,
            stream_id=stream_id,
            request={"request": request},
            method=self.generate_response,
        )
        return JSONResponse({"stream_url": f"/stream_response?stream_id={stream_id}"})

    async def stream_response(self, stream_id: str) -> StreamingResponse:
        """
        Streams the response of the model

        Args:
            stream_id (str): The ID of the stream

        Returns:
            StreamingResponse: The response stream
        """
        if not self.last_response_stream:
            return JSONResponse(
                {"message": "No stream available with the given ID"},
                status_code=404,
            )

        response = StreamingResponse(
            self.last_response_stream.method(**self.last_response_stream.request),
            media_type=self.last_response_stream.media_type,
        )

        self.last_response_stream = None

        return response

    async def generate_response(
        self, request: ThinkingRequest
    ) -> AsyncGenerator[str, None]:
        """
        Generates the response to the question

        Args:
            request (ThinkingRequest): The request to generate a response

        Yields:
            str: The response to the question
        """
        template = """{question}"""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.model

        async for chunk in chain.astream({"question": request.text}):
            yield chunk  # Send each chunk of response as it arrives
