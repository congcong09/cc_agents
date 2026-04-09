import json
import re

from core.agent import Agent
from core.config import Config
from core.exceptions import AgentException
from core.llm import CCAgentsLLM, ChatMessage

DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```json
["步骤1", "步骤2", "步骤3", ...]
```
"""

DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan_list}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""


class Planner:
    def __init__(self, llm_client: CCAgentsLLM):
        self.name = "Planner"
        self.llm_client = llm_client

    def plan(self, input_text: str, **kwargs):
        messages: list[ChatMessage] = [{"role": "user", "content": input_text}]

        response = self.llm_client.invoke(messages=messages, **kwargs)

        plan_list = self._extract_plan(response_text=response)

        return plan_list

    def _extract_plan(self, response_text: str):
        match = re.search(r"```json\s*(.*?)\s*```", response_text)
        if match:
            plan_str = match.group(1).strip()
        else:
            plan_str = "[]"

        try:
            return json.loads(plan_str)
        except Exception:
            return []


class Executor:
    def __init__(
        self,
        llm_client: CCAgentsLLM,
    ):
        self.name = "executor"
        self.llm_client = llm_client

    def execute(self, input_text: str, **kwargs):
        pass


class PlanSolveAgent(Agent):
    def __init__(
        self,
        name: str,
        llm: CCAgentsLLM,
        system_prompt: str | None = None,
        config: Config | None = None,
        custom_prompts: dict[str, str] | None = None,
    ):
        super().__init__(name, llm, system_prompt, config)

        if custom_prompts:
            self.planner_prompt = custom_prompts.get("planner", DEFAULT_PLANNER_PROMPT)
            self.executor_prompt = custom_prompts.get(
                "executor", DEFAULT_PLANNER_PROMPT
            )
        else:
            self.planner_prompt = DEFAULT_PLANNER_PROMPT
            self.executor_prompt = DEFAULT_EXECUTOR_PROMPT

        self.planner = Planner(llm_client=self.llm)
        self.executor = Executor(llm_client=self.llm)

    def run(self, input_text: str, **kwargs) -> str:
        print(f"🤖 {self.name} 开始处理问题：{input}")

        full_planner_prompt = self.planner_prompt.format(question=input_text)

        plan_list = self.planner.plan(full_planner_prompt)

        if not plan_list:
            raise AgentException("Planner未生成计划列表，无法继续执行")

        history = []
        for idx, plan in enumerate(plan_list):
            print(f"🏃‍♀️ 正在执行计划第{idx}项：{plan}")
            full_executor_prompt = self.executor_prompt.format(
                question=input_text,
                plan_list=plan_list,
                history=history,
                current_step=idx + 1,
            )

            response = self.executor.execute(full_executor_prompt)
            history.append(f"[步骤：{idx + 1}] 结果：{response}")
