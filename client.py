import requests
from rich import print

from thinking_neuron.models import ServerConfigRequest, ModelSettings

# HOST = "http://192.168.1.140:8000"
HOST = "http://0.0.0.0:8000"
url = f"{HOST}/think"

# response = requests.post(url, json={"text": "What's up dude?"}, stream=True)
# for chunk in response.iter_content(chunk_size=1024):
#     if chunk:
#         print(chunk.decode(), end="", flush=True)

UPDATE_SETTINGS_URL = f"{HOST}/update_settings"

model_settings = ModelSettings(model="deepseek-r1:14b")
data = ServerConfigRequest(
    name="bob",
).model_dump()

print(data)

result = requests.post(UPDATE_SETTINGS_URL, json=data)

print(result.json())
