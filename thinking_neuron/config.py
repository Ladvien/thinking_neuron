from dataclasses import dataclass, asdict
from pydantic import BaseModel


class ModelSettings(BaseModel):
    model: str


class ThinkerConfig(BaseModel):
    name: str
    model_settings: ModelSettings
