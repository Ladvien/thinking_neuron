from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from typing import AsyncGenerator
from uuid import uuid4
import ollama

from thinking_neuron.models.request import StreamResultRequest
from thinking_neuron.models.state import Stream

from .models import ThinkingResponse, OllamaErroResponse, UpdateConfigResponse
from .models import (
    ThinkingServerConfig,
    ServerConfigRequest,
    ThinkingRequest,
)


class ThinkingNeuronServer:

    def __init__(self, config: ThinkingServerConfig = None) -> None:
        if config:
            self.current_config = config
        else:
            self.current_config = ThinkingServerConfig()

        self.last_response_stream = None

        self._setup_llm(self.current_config)

        self.router = APIRouter()

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
            "/list_models",
            self.list_models,
            methods=["GET"],
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
        response = self._setup_llm(request)
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
            request=request,
            method=self.generate_response,
        )
        return JSONResponse({"stream_id": f"/stream_response?stream_id={stream_id}"})

    async def stream_response(self, stream_id: str) -> StreamingResponse:
        """
        Streams the response of the model

        Args:
            stream_id (str): The ID of the stream

        Returns:
            StreamingResponse: The response stream
        """
        response = StreamingResponse(
            self.last_response_stream.method(self.last_response_stream.request),
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

    def _setup_llm(
        self, config: ThinkingServerConfig
    ) -> UpdateConfigResponse | JSONResponse:

        try:
            available_models = ollama.ps()
        except ConnectionError as e:
            print("asd")
            return OllamaErroResponse()

        if config.model_settings.model not in available_models:
            progress = ollama.pull(config.model_settings.model)

        self.model = OllamaLLM(
            **config.model_settings.model_dump(),
        )
        print(self.model)
        self.current_config = config

        return JSONResponse(
            content=UpdateConfigResponse(
                **self.current_config.model_settings.model_dump(),
            ).model_dump(),
        )
