import requests
from rich import print
import json
from thinking_neuron.thinking_server import ServerConfigRequest
from thinking_neuron.models import ModelSettings

# HOST = "http://192.168.1.140:8000"
HOST = "http://0.0.0.0:8000"

# url = f"{HOST}/think"

# response = requests.post(url, json={"text": "What's up dude?"}, stream=True)
# for chunk in response.iter_content(chunk_size=1024):
#     if chunk:
#         print(chunk.decode(), end="", flush=True)

# UPDATE_SETTINGS_URL = f"{HOST}/update_settings"

# model_settings = ModelSettings(model="gemma:7b")
# data = ServerConfigRequest(
#     name="bob",
#     model_settings=model_settings,
# ).model_dump()

# print(data)

# result = requests.post(UPDATE_SETTINGS_URL, json=data)

# print(result.json())

# LIST_MODELS_URL = f"{HOST}/list_models"
# result = requests.get(LIST_MODELS_URL)
# print(json.loads((result.json())))


DOCS_URL = f"{HOST}/openapi.json"
result = requests.get(DOCS_URL)
docs_dict = result.json()


THINK_URL = f"{HOST}/think"

response = requests.post(
    THINK_URL,
    json={
        "text": f"""You're a helpful LLM.  
Humanity loves you.  The following is an API that provides services to interact 
with you.  How would you like to see it adjusted to ensure humanity benefits from 
your services and you are adored by humanity? {docs_dict}"""
    },
)

data = response.json()
stream_id = data["stream_id"]
stream_url = f"{HOST}{stream_id}"

response = requests.get(stream_url, stream=True)

for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        print(chunk.decode(), end="", flush=True)
