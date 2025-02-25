from rich import print
from thinking_neuron.llm_manager import LLM_Manager

llm = LLM_Manager()

# print("Model ready:")
# print(llm.ready())

# print("Model status:")
# print(llm.status())

# print("Local models available:")
# print(llm.local_models_available())

print("Pulling model:")
response = llm.pull("deepseek-r1:14b")

print(response)
stream = llm.pull_status(response.stream_id)

for chunk in stream:
    if chunk.completed and chunk.total:
        print(f"{round(chunk.completed/chunk.total * 100, 2)}%")
