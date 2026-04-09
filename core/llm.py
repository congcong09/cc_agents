import os
from typing import Literal, TypeAlias

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from core.exceptions import LLMException

SUPPORT_PROVIDERS = Literal["openai", "deepseek", "zhipu", "qwen"]

Message: TypeAlias = ChatCompletionMessageParam


class CCAgentsLLM:
    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        provider: SUPPORT_PROVIDERS | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        timeout: int | None = None,
        **kwargs,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", "60"))

        self.kwargs = kwargs

        if not all([self.model, self.api_key, self.base_url]):
            raise LLMException("需要提供模型名，api_key，base_url")

        self._client = self._create_client()

    def _create_client(self):
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def think(self, messages: list[Message], temperature: float | None = None):
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self._client.chat.completions.create(
                model=self.model or "",
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )

            for thunk in response:
                content = thunk.choices[0].delta.content or ""
                if content:
                    print(content, end="", flush=True)
                    yield content

            print()
        except Exception as e:
            err_msg = f"❌ 调用LLM API时发生错误：{e}"
            print(err_msg)
            raise LLMException(err_msg)

    def invoke(self, messages: list[Message], **kwargs):
        try:
            response = self._client.chat.completions.create(
                model=self.model or "",
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["temperature", "max_tokens"]
                },
            )

            return response.choices[0].message.content
        except Exception as e:
            raise LLMException(f"LLM 调用失败 {e}")

    def stream_invoke(self, messages: list[Message], **kwargs):
        try:
            response = self._client.chat.completions.create(
                model=self.model or "",
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in ["temperature", "max_tokens", "stream"]
                },
            )
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                if content:
                    print(content, end="", flush=True)
                    yield content
            print()
        except Exception as e:
            raise LLMException(f"LLM 调用失败 {e}")
