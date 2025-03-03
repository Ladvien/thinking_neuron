from dataclasses import dataclass
from .thinking_server import ThinkingToolServer

import os
import logging
from rich.logging import RichHandler

logging.basicConfig(
    filename="thinking.log",
    format="%(asctime)s - %(pathname)s - %(levelname)s - %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
logger.addHandler(RichHandler())
