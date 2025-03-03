from rich import print
import logging
import os
import yaml
from fastapi import FastAPI
import uvicorn

from thinking_tool.thinking_server import ThinkingToolServer

app = FastAPI()

speech_neuron = ThinkingToolServer()
app.include_router(speech_neuron.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
