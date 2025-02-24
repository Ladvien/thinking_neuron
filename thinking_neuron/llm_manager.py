from fastapi.responses import JSONResponse
from langchain_ollama.llms import OllamaLLM
from uuid import uuid4
import ollama

from thinking_neuron.models.request import StreamResultRequest
from thinking_neuron.models.response import OllamaPullModelStreamResponse
from thinking_neuron.models.state import Stream

from .models import OllamaErroResponse, UpdateConfigResponse
from .models import (
    ThinkingServerConfig,
    ServerConfigRequest,
)


class LLM_Manager:

    def __init__(self, config: ThinkingServerConfig = None) -> None:
        self.config = config if config else ThinkingServerConfig()

    def update_settings(
        self, request: ServerConfigRequest
    ) -> UpdateConfigResponse | JSONResponse:

        try:
            available_models = ollama.ps()
        except ConnectionError as e:
            return OllamaErroResponse(error_msg=str(e))

        if self.config.model_settings.model not in available_models:
            stream_id = str(uuid4())
            self.last_response_stream = Stream(
                text=f"Pulling model {self.config.model_settings.model}",
                stream_id=stream_id,
                request={"request": StreamResultRequest(stream_id=str(uuid4()))},
                method=ollama.pull,
            )
            return OllamaPullModelStreamResponse(
                stream_id=f"/stream_response?stream_id={stream_id}"
            )

        self.model = OllamaLLM(
            **self.config.model_settings.model_dump(),
        )
        print(self.model)
        self.config = self.config

        return JSONResponse(
            content=UpdateConfigResponse(
                **self.config.model_settings.model_dump(),
            ).model_dump(),
        )
