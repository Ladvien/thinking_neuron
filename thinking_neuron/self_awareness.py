from pathlib import Path
from pydantic import BaseModel, Field
import os
from glob import glob
import logging
from rich import print

logger = logging.getLogger(__name__ + "." + __file__)


class CodeFile(BaseModel):
    name: str
    content: str


class LogFile(BaseModel):
    name: str
    content: str


class SelfAwareness:
    code_directory: str

    log_directory: str
    log_filename: str = "thinking.log"
    log_filepath: str | None = None

    def __init__(
        self, code_directory: str = "thinking_neuron", log_directory: str = ".."
    ) -> None:
        super().__init__()
        self.code_directory = code_directory
        self.log_filepath = Path(__file__).parent / log_directory / self.log_filename

    def _load_code(self):
        pattern = "../" + self.code_directory + "/*.py"
        logger.info(f"Looking for code files in '{pattern}'")
        file_paths = glob(pattern, recursive=True)
        logger.info("Found code files:")
        logger.info(file_paths)

        code_files = []

        for code_path in file_paths:
            with open(code_path, "r") as f:
                content = f.read()
                code_files.append(CodeFile(name=code_path, content=content))

        if code_files is None or len(code_files) == 0:
            logger.error("No code files found")

        logger.info(f"Loaded code files: {len(code_files)}")

        return code_files

    def _load_logs(self):
        with open(self.log_filepath, "r") as f:
            content = f.read()
            return content

    def code_file(self, name: str) -> CodeFile:
        if name is None:
            return None

        for code_file in self._load_code():
            if code_file.name == name:
                return code_file

    def all_code_files(self) -> list[CodeFile]:
        return self._load_code()

    def all_log_files(self) -> list:
        return self._load_logs()
