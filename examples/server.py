from rich import print
import logging
import os
import yaml
from fastapi import FastAPI
import uvicorn

from thinking_tool.thinking_server import ThinkingToolServer

app = FastAPI()

thinking_tool = ThinkingToolServer()
app.include_router(thinking_tool.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
