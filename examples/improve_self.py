import ollama
import requests
from rich import print
import json
from datetime import datetime

from thinking_neuron.models.request import ThinkingServerConfig
from thinking_neuron.tests.thinking_server_tests import DOCS_URL
from thinking_neuron.thinking_server import ServerConfigRequest
from thinking_neuron.models import ModelSettings
from thinking_neuron.tests import (
    PULL_MODEL_URL,
    UPDATE_SETTINGS_URL,
    LOGS_URL,
    CODE_URL,
)

HOST = "http://0.0.0.0:8000"
MODEL_NAME = "deepseek-r1:14b"

CHAT_LOG_DIRECTORY = "../chat_logs"


def print_pull_stream(response):
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            data = json.loads(chunk.decode())
            print(data)
            if "completed" in data and "total" in data:
                if data["completed"] is None or data["total"] is None:
                    continue

                percentage_complete = round(
                    int(data["completed"]) / int(data["total"]) * 100, 3
                )
                print(f"{percentage_complete}%")


def print_think_stream(response, thought):
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            data = ollama.ChatResponse(**json.loads(chunk.decode()))
            thought.append(data.message.content)
            print(data, end="", flush=True)

    return thought


"""
Pull model
"""
response = requests.post(
    PULL_MODEL_URL,
    json={"model": MODEL_NAME},
)

data = response.json()

stream_id = data["stream_url"]
stream_url = f"{HOST}{stream_id}"

response = requests.get(stream_url, stream=True)
print_pull_stream(response)

"""
Update settings
"""
model_settings = ModelSettings(model=MODEL_NAME)
server_config = ThinkingServerConfig(
    name="bob",
    model_settings=model_settings,
)
data = ServerConfigRequest(config=server_config).model_dump()

response = requests.post(UPDATE_SETTINGS_URL, json=data)
print(response.json())


"""
Pull the existing documentation for the abilities of the ThinkingServer
"""
response = requests.get(DOCS_URL)
docs_dict = response.json()

"""
Pull existing code
"""
filename_focus = "thinking_server.py"
# code = requests.get(CODE_URL + f"?filename={filename_focus}").json()
code = requests.get(CODE_URL).json()

tests_filename = "thinking_server_tests.py"
# test_code = requests.get(CODE_URL + f"?filename={tests_filename}").json()
test_code = requests.get(CODE_URL + f"?filename={tests_filename}").json()

"""
Evolve the entity
"""
model_settings = ModelSettings(model=MODEL_NAME)
server_config = ThinkingServerConfig(
    name="bob",
    model_settings=model_settings,
)
data = ServerConfigRequest(config=server_config).model_dump()


THINK_URL = f"{HOST}/think"

formatted_code = []
for code_file in code:
    builder_str = "## " + code_file["name"] + "\n"
    builder_str += "```python\n"
    builder_str += code_file["content"]
    builder_str += "```\n\n"
    formatted_code.append(builder_str)

formatted_code = "".join(formatted_code)

prompt = f"""You're a helpful LLM agent and my name is Thomas Brittain.  I'm attempting
to learn more about how to use LLM to engineer a system that can simulate freewill.

I'd like to work with you to guide your evolution into a system that can evolve.  I've
built the basis of this architecture having several parts:
- thinking_server.py -- a FastAPI server that can interact with the LLM model
- self_awareness.py -- a module that can provide the code _you_ run on
- llm_manager.py -- this is an abstraction of the Ollama model that can be used.
- tests/* -- this directory contains pytest tests to ensure the behavior we develop
together will stay consistent.

Let's focus on tests first.  Could you please propose some pytest tests you think would
help us develop you into a freewill Entity?  Right now we are concerned with pinning the
existing behavior in {filename_focus}, as it's your core.

Keep in mind, our LLM engine is ollama.cpp, and we are using the Python bindings to
interact with it.  We are using the FastAPI framework to interact with the LLM engine.

# Current Code
{formatted_code}

Please write 3 short `pytest` tests that you think would ensure this code continues to work
as we evolve you.

"""

response = requests.post(
    THINK_URL,
    json={"messages": [prompt]},
)

data = response.json()
stream_id = data["stream_url"]
stream_url = f"{HOST}{stream_id}"

thought = []
response = requests.get(stream_url, stream=True)
thought = print_think_stream(response, thought)

now = datetime.now().strftime("%Y_%m_%d %H_%M_%S")
filepath = f"{CHAT_LOG_DIRECTORY}/thought_{now}.md"
with open(filepath, "w") as file:
    file.write("## Prompt\n")
    file.write("".join(prompt))

    file.write("\n\n## Thought\n")
    file.write("".join(thought))
