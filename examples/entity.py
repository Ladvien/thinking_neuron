import requests

from thinking_tool.entity import Entity, Tool, ToolConfig
from thinking_tool.thinking_server import ThinkingToolServer


class ThinkingTool(Tool):
    def available_actions(self) -> list[str]:
        return requests.get(
            f"http://{self.tool_config.host}:{self.tool_config.port}/openapi.json"
        ).json()

    def act(self, action: str) -> str:
        raise NotImplementedError


thinking_server = ThinkingTool(
    ToolConfig(
        name="Thinking Neuron",
        description="Does the thing",
        host="0.0.0.0",
        port=8000,
    )
)


entity = Entity(
    directive="Make yourself better.",
    tools=[thinking_server],
)
