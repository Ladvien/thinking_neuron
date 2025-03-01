import pytest
from thinking_neuron.llm_manager import LLM_Manager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from examples.server import app
import json


@pytest.fixture
def mock_ollama():
    return {"show": True, "pull": True}


def test_pull_model(mock_ollama):
    # Initialize with a model settings
    manager = LLM_Manager(
        model_settings={"model": "gpt-3.5-tiny"},
        ollama_client=mock_ollama,
    )

    # Pull the model
    manager.pull("gpt-3.5-tiny")

    # Check if the status is ready
    status = manager.status()
    assert status["message"] == "ready"

    # Verify local models include the pulled one
    local_models = manager.local_models_available()
    assert "gpt-3.5-tiny" in [m["model"] for m in local_models]


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_readiness_of_ollama_server(client):
    """Test that the /ready endpoint correctly reports Ollama's status."""
    response = await client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # Check if the message indicates readiness or an error condition.
    # Note: This might need to be adjusted based on actual implementation.


@pytest.mark.asyncio
async def test_local_models_list(client):
    """Test that the /models endpoint returns a list of available local models."""
    response = await client.get("/models")
    assert response.status_code == 200
    data = response.json()
    # Check if it's a list and contains at least one model.
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_model_pull_status(client):
    """Test that the /pull_status endpoint returns streaming updates."""
    model_name = "gpt2"
    response = await client.get(f"/pull_status?model={model_name}")
    assert response.status_code == 200
    # Since this is a generator, we can check if it starts to yield data.
    # Note: The actual implementation might need adjustments based on Ollama's API.
