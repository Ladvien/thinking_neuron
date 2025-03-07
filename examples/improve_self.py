import ollama
from rich import print
import json

from thinking_tool.models.request import (
    OllamaSettings,
    PullModelRequest,
    ServerConfigRequest,
    ThinkingServerConfig,
)
from thinking_tool.thinking_client import ThinkingToolClient

HOST = "http://0.0.0.0:8000"
MODEL_NAME = "deepseek-r1:14b"

CHAT_LOG_DIRECTORY = "thinking_tool/../chat_logs"

client = ThinkingToolClient(base_url=HOST)

"""
Pull model
"""
response = client.pull_model(PullModelRequest(model=MODEL_NAME))

for chunk in response:
    print(chunk)

"""
Update settings
"""
model_settings = OllamaSettings(model=MODEL_NAME)
server_config = ThinkingServerConfig(
    name="bob",
    model_settings=model_settings,
)

response = client.update_settings(ServerConfigRequest(config=server_config))
print(response)


# """
# Pull the existing documentation for the abilities of the ThinkingServer
# """
# response = requests.get(DOCS_URL)
# docs_dict = response.json()

# """
# Pull existing code
# """
# filename_focus = "thinking_server.py"
# # code = requests.get(CODE_URL + f"?filename={filename_focus}").json()
# code = requests.get(CODE_URL).json()

# tests_filename = "thinking_server_tests.py"
# # test_code = requests.get(CODE_URL + f"?filename={tests_filename}").json()
# test_code = requests.get(CODE_URL + f"?filename={tests_filename}").json()

# """
# Evolve the entity
# """
# model_settings = ModelSettings(model=MODEL_NAME)
# server_config = ThinkingServerConfig(
#     name="bob",
#     model_settings=model_settings,
# )
# data = ServerConfigRequest(config=server_config).model_dump()


# THINK_URL = f"{HOST}/think"

# formatted_code = []
# for code_file in code:
#     builder_str = "## " + code_file["name"] + "\n"
#     builder_str += "```python\n"
#     builder_str += code_file["content"]
#     builder_str += "```\n\n"
#     formatted_code.append(builder_str)

# formatted_code = "".join(formatted_code)

# prompt = f"""You're a helpful LLM agent and my name is Thomas Brittain.  I'm attempting
# to learn more about how to use LLM to engineer a system that can simulate freewill.

# Could you please look over this OpenAPI definition and create a Python client that can
# interact with the server?

# ```json
# {docs_dict}
# ```
# """

# response = requests.post(
#     THINK_URL,
#     json={"messages": [prompt]},
# )

# data = response.json()
# stream_id = data["stream_url"]
# stream_url = f"{HOST}{stream_id}"

# thought = []
# response = requests.get(stream_url, stream=True)
# thought = print_think_stream(response, thought)

# now = datetime.now().strftime("%Y_%m_%d %H_%M_%S")

# os.makedirs(CHAT_LOG_DIRECTORY, exist_ok=True)

# filepath = f"{CHAT_LOG_DIRECTORY}/thought_{now}.md"
# filepath = os.path.abspath(filepath)

# with open(filepath, "w") as file:
#     file.write("## Prompt\n")
#     file.write("".join(prompt))

#     file.write("\n\n## Thought\n")
#     file.write("".join(thought))
