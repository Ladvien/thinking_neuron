from dataclasses import dataclass


@dataclass
class ModelConfig:
    model: str


@dataclass
class ThinkerConfig:

    name: str
    model_config: ModelConfig
