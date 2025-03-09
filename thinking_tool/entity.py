from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass
from time import sleep
from rich import print

logger = logging.getLogger(__name__ + "." + __file__)


@dataclass
class ToolConfig:
    name: str
    description: str
    host: str
    port: int


class Tool(ABC):

    def __init__(self, tool_config: ToolConfig):
        self.tool_config = tool_config

    @abstractmethod
    def available_actions(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def act(self, action: str) -> str:
        raise NotImplementedError


class Entity:

    def __init__(
        self,
        directive: str,
        thinking_server: Tool,
        tools: list[Tool],
    ):
        self.directive = directive
        self.thinking_server = thinking_server
        self.tools = tools

        while True:
            self.think()
            sleep(1)

    def think(self):
        logger.info(f"Entity thinking about: {self.directive}")

        thinking_tool = self.tools[0]

        for tool in self.tools:
            actions = tool.available_actions()
            print(type(actions))
            print(f"Available actions: {actions}")
