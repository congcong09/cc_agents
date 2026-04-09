from abc import ABC, abstractmethod

from core.config import Config
from core.llm import CCAgentsLLM

from .message import Message


class Agent(ABC):
    def __init__(
        self,
        name: str,
        llm: CCAgentsLLM,
        system_prompt: str | None = None,
        config: Config | None = None,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config
        self._history: list[Message] = []

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        pass

    def _prepare_messages(self, input_text: str):
        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": input_text})

        return messages

    def add_message(self, message: Message):
        self._history.append(message)

    def clear_history(self):
        self._history.clear()

    def get_history(self):
        return self._history.copy()

    def __str__(self):
        # TODO: 需要更详细的信息
        return f"Agent({self.name})"

    def __repr__(self):
        return self.__str__()
