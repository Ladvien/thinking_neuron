from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from typing import AsyncGenerator
from uuid import uuid4
import ollama
import logging
from rich import print
import json

from thinking_neuron.self_awareness import SelfAwareness

from .llm_manager import LLM_Manager
from .models import UpdateConfigResponse
from .models import ServerConfigRequest, ThinkingRequest, PullModelRequest, Stream

logger = logging.getLogger(__name__ + "." + __file__)


class ThinkingNeuronServer:

    def __init__(self) -> None:

        self.last_response_stream = None

        self.llm_mang = LLM_Manager()
        self.self_awareness = SelfAwareness()

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

        self.router.add_api_route(
            "/logs",
            self.logs,
            methods=["GET"],
            response_class=JSONResponse,
        )

        self.router.add_api_route(
            "/code",
            self.code,
            methods=["GET"],
            response_class=JSONResponse,
        )

    async def list_models(self) -> JSONResponse:
        """
        Lists all available models

        Returns:
            JSONResponse: A response containing the list
        """
        models = self.llm_mang.local_models_available().models
        logger.info("Local models available:")
        logger.info(models)
        return JSONResponse(models)

    async def pull_model(self, request: PullModelRequest) -> JSONResponse:
        """
        Pulls a model from the ollama service

        Args:
            model (str): The model to pull

        Returns:
            JSONResponse: The response of the pull
        """

        stream_id = str(uuid4())

        # Don't wait, start pulling the model.
        _ = self.llm_mang.pull(request.model)

        # Setup stream callback.
        self.last_response_stream = Stream(
            text=f"Attempting to download model: '{request.model}'",
            stream_id=stream_id,
            request={"request": request},
            method=self._pull_stream,
        )

        return JSONResponse({"stream_url": f"/stream_response?stream_id={stream_id}"})

    async def update_settings(
        self, request: ServerConfigRequest
    ) -> UpdateConfigResponse:
        return JSONResponse(self.llm_mang.update(request).model_dump_json())

    async def think(self, request: ThinkingRequest) -> StreamingResponse:
        stream_id = str(uuid4())
        self.last_response_stream = Stream(
            text=request.text,
            stream_id=stream_id,
            request={"request": request},
            method=self._think_stream,
        )
        return JSONResponse({"stream_url": f"/stream_response?stream_id={stream_id}"})

    async def stream_response(self, stream_id: str) -> StreamingResponse:
        if not self.last_response_stream:
            return JSONResponse(
                {"message": "No stream available with the given ID"},
                status_code=404,
            )

        if self.last_response_stream.stream_id != stream_id:
            return JSONResponse(
                {"message": "No stream available with the given ID"},
                status_code=404,
            )

        print(self.last_response_stream.method)
        print(self.last_response_stream.request)

        stream = self.last_response_stream.method(**self.last_response_stream.request)
        response = StreamingResponse(
            stream,
            media_type=self.last_response_stream.media_type,
        )

        self.last_response_stream = None

        return response

    async def _think_stream(
        self, request: ThinkingRequest
    ) -> AsyncGenerator[str, None]:
        template = """{question}"""
        prompt = ChatPromptTemplate.from_template(template)

        chain = prompt | self.llm_mang.model

        async for chunk in chain.astream({"question": request.text}):
            yield chunk  # Send each chunk of response as it arrives

    async def _pull_stream(
        self, request: PullModelRequest
    ) -> AsyncGenerator[str, None]:

        if not self.last_response_stream:
            return

        if self.last_response_stream.stream_id != request.stream_id:
            return

        stream = self.last_response_stream.method(**self.last_response_stream.request)

        async for chunk in stream:
            yield chunk  # Send each chunk of response as it arrives

    async def logs(self) -> JSONResponse:
        logs = self.self_awareness.all_log_files()
        return JSONResponse(logs)

    async def code(self) -> JSONResponse:
        code = self.self_awareness.all_code_files()

        return JSONResponse([c.model_dump() for c in code])
