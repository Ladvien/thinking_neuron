from rich import print
from thinking_neuron.llm_manager import LLM_Manager

llm = LLM_Manager()

# print("Model ready:")
# print(llm.ready())

# print("Model status:")
# print(llm.status())

# print("Local models available:")
# print(llm.local_models_available())

"""
Setup an asyncio loop to run the server
"""


print("Pulling model:")
response = llm.pull("deepseek-r1:14b")  # Ensure this is an async function

print(response)
stream = llm.pull_status("deepseek-r1:14b")  # Ensure this is an async function
for chunk in stream:
    if chunk.completed and chunk.total:
        print(f"{round(chunk.completed / chunk.total, 3) * 100}%")
