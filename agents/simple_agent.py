from typing import Iterator

from core.agent import Agent
from core.config import Config
from core.llm import CCAgentsLLM
from core.message import Message


class SimpleAgent(Agent):
    def __init__(
        self,
        name: str,
        llm: CCAgentsLLM,
        system_prompt: str | None = None,
        config: Config | None = None,
    ):
        super().__init__(name, llm, system_prompt, config)

    def run(self, input_text: str, **kwargs) -> str:
        # 发送给 llm 的 messages 列表
        messages = self._prepare_messages(input_text)

        response = self.llm.invoke(messages=messages, **kwargs)

        # 本地保存的 message 列表，保存有更多的信息
        self.add_message(Message(role="user", content=input_text))
        self.add_message(Message(role="assistant", content=response))

        return response

    def stream_run(self, input_text: str, **kwargs) -> Iterator[str]:

        messages = self._prepare_messages(input_text)

        response = self.llm.stream_invoke(messages=messages, **kwargs)
        full_response = ""
        for chunk in response:
            full_response += chunk
            yield chunk

        self.add_message(Message(role="user", content=input_text))
        self.add_message(Message(role="assistant", content=full_response))
