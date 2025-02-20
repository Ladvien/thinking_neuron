from rich import print
import logging
import os
import yaml
from fastapi import FastAPI
import uvicorn


from thinking_neuron import ThinkerConfig, ThinkingNeuronServer


CONFIG_PATH = os.environ.get("NODE_CONFIG_PATH", "config.yaml")
config = ThinkerConfig(**yaml.safe_load(open(CONFIG_PATH, "r")))

app = FastAPI()

speech_neuron = ThinkingNeuronServer(config)
app.include_router(speech_neuron.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
