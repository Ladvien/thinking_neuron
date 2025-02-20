import requests

HOST = "http://0.0.0.0:8000"
url = f"{HOST}/think"

response = requests.post(url, json={"text": "What's up dude?"}, stream=True)

for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        print(chunk.decode(), end="", flush=True)
