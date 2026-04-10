from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolParameter(BaseModel):
    """工具参数定义"""

    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class Tool(ABC):
    def __init__(self, name: str, description: str, parameters: list[ToolParameter]):
        self.name = name
        self.description = description
        self.parameters = parameters

    @abstractmethod
    def run(self, parameters: dict[str, Any]) -> str:
        pass

    def get_parameters(self) -> list[ToolParameter]:
        return self.parameters

    def validate_parameters(self, parameters: dict[str, Any]) -> bool:
        required_params = [p.name for p in self.parameters if p.required]
        return all(p for p in parameters if p in required_params)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [param.model_dump() for param in self.parameters],
        }

    def __str__(self) -> str:
        return f"Tool(name={self.name})"

    def __repr__(self) -> str:
        return self.__str__()
