import requests

# from dataclasses import dataclass
from typing import Optional, List, Dict

from thinking_tool.models.request import (
    PullModelRequest,
    ServerConfigRequest,
    ThinkingRequest,
)
from thinking_tool.models.response import ThinkingResponse, UpdateConfigResponse


class ThinkingToolClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def _get(self, endpoint: str, params: Optional[Dict] = None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, json_data: Dict):
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=json_data)
        response.raise_for_status()
        return response.json()

    # Implement /list_models endpoint
    def list_models(self) -> List[str]:
        """
        Lists available models.
        Returns:
            List of model names/ids.
        """
        return self._get("/list_models")

    # Implement /pull_model endpoint
    def pull_model(self, request: PullModelRequest) -> Dict:
        """
        Pulls a specified model.
        Args:
            request: PullModelRequest containing the model name/id.
        Returns:
            Response containing status and message.
        """
        return self._post("/pull_model", {"model": request.model})

    # Implement /think endpoint
    def think(self, request: ThinkingRequest) -> ThinkingResponse:
        """
        Initiates a thinking process with given messages.
        Args:
            request: ThinkingRequest containing messages for the LLM to process.
        Returns:
            Response containing the generated response.
        """
        return self._post("/think", {"messages": request.messages})

    # Implement /update_settings endpoint
    def update_settings(self, request: ServerConfigRequest) -> UpdateConfigResponse:
        """
        Updates server settings with specified configuration.
        Args:
            request: ServerConfigRequest containing the new configuration.
        Returns:
            Response containing the stream_id.
        """
        response_json = self._post("/update_settings", request.config)
        return UpdateConfigResponse(**response_json)

    # Implement /stream_response endpoint
    def stream_response(self, stream_id: str) -> Dict:
        """
        Streams a response for a given stream_id.
        Args:
            stream_id: The ID of the stream to monitor.
        Returns:
            Streamed response containing messages as they are generated.
        """
        return self._get("/stream_response", {"stream_id": stream_id})

    # Implement /logs endpoint
    def get_logs(self) -> Dict:
        """
        Retrieves server logs.
        Returns:
            Dictionary containing log information.
        """
        return self._get("/logs")

    # Implement /code endpoint
    def get_code(self, filename: Optional[str] = None) -> Dict:
        """
        Retrieves source code from the server.
        Args:
            filename: Optional. The name of the file to retrieve.
        Returns:
            Dictionary containing the requested code or list of files if no filename is provided.
        """
        params = {"filename": filename} if filename else None
        return self._get("/code", params)
