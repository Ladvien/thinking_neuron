import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from typing import AsyncGenerator
from uuid import uuid4
import logging
from rich import print

from thinking_tool.models.request import StreamRequest, ThinkingServerConfig

from .self_awareness import SelfAwareness
from .llm_manager import OllamaLLM_Manager
from .models import ServerConfigRequest, ThinkingRequest, PullModelRequest

logger = logging.getLogger(__name__ + "." + __file__)


class ThinkingToolServer:

    def __init__(
        self,
        config: ThinkingServerConfig = None,
        # Relative path to the code directory.
        code_dir: str = "../thinking_tool",
    ) -> None:
        self.config = config if config else ThinkingServerConfig()

        self.code_dir = code_dir
        self.last_response_stream = None

        self.llm_mang = OllamaLLM_Manager(config=self.config)
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

        logger.info("ThinkingToolServer initialized")

    async def list_models(self) -> JSONResponse:
        models = self.llm_mang.local_models_available().models
        logger.info("Local models available:")
        logger.info(models)
        return JSONResponse(models)

    async def pull_model(self, request: PullModelRequest) -> JSONResponse:
        stream_id = str(uuid4())

        # Don't wait, start pulling the model.
        logger.info(f"Started pulling model: '{request.model}'")
        _ = self.llm_mang.pull(request.model)

        # # Setup stream callback.
        self.last_response_stream = StreamRequest(
            text=f"Attempting to download model: '{request.model}'",
            stream_id=stream_id,
            request={"request": request},
            method=self._pull_stream,
        )

        return JSONResponse({"stream_url": f"/stream_response?stream_id={stream_id}"})

    async def update_settings(self, request: ServerConfigRequest) -> JSONResponse:
        response = self.llm_mang.update(request.config)
        if response.message == "Model updated":
            return JSONResponse(request.config.model_dump())

        return JSONResponse(status_code=404, content=response.model_dump())

    async def think(self, request: ThinkingRequest) -> StreamingResponse:
        stream_id = str(uuid4())
        self.last_response_stream = StreamRequest(
            stream_id=stream_id,
            request={"request": request},
            method=self._think_stream,
        )
        return JSONResponse({"stream_url": f"/stream_response?stream_id={stream_id}"})

    async def stream_response(self, stream_id: str) -> StreamingResponse:
        print(stream_id)
        print(self.last_response_stream)
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
        async for chunk in self.llm_mang.generate(request.messages):
            logger.info(chunk.model_dump_json())
            yield chunk.model_dump_json()

    async def _pull_stream(
        self, request: PullModelRequest
    ) -> AsyncGenerator[str, None]:
        async for chunk in await self.llm_mang.pull_status(request.model):
            data = chunk.model_dump()
            yield json.dumps(data) + "\n"

    async def logs(self) -> JSONResponse:
        logs = self.self_awareness.all_log_files()
        return JSONResponse(logs)

    async def code(self, filename: str = None) -> JSONResponse:
        if filename:
            code = self.self_awareness.code_file(filename)
            if code is None:
                return JSONResponse(
                    {"message": f"No code file found with name: '{filename}'"},
                    status_code=404,
                )

            return JSONResponse(code.model_dump())

        code = self.self_awareness.all_code_files()
        return JSONResponse([c.model_dump() for c in code])
