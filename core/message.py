from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

MessageRole = Literal["user", "assistant", "system", "tool"]


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime | None = Field(default_factory=datetime.now)
    metadata: dict[str, Any] | None = Field(default_factory=dict)

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }

    def __str__(self):
        return f"[{self.role}] {self.content}"
