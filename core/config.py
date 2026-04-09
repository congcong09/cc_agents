import os

from pydantic import BaseModel


class Config(BaseModel):
    default_model: str = "qwen3.5-plus"
    default_provider: str = "dashscope"
    temperature: float = 0.7
    max_tokens: int | None = None

    debug: bool = False
    log_level: str = "INFO"

    max_history_length: int = 100

    @classmethod
    def from_env(cls) -> "Config":
        max_tokens_str = os.getenv("MAX_TOKENS")
        if max_tokens_str:
            try:
                max_tokens = int(max_tokens_str)
            except Exception:
                max_tokens = None
        else:
            max_tokens = None
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=max_tokens,
        )

    def to_dict(self):
        return self.model_dump()
