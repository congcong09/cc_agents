import json
import re

from core.agent import Agent
from core.config import Config
from core.llm import CCAgentsLLM, ChatMessage
from core.message import Message

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
    def __init__(self, llm_client: CCAgentsLLM, instruction_prompt: str):
        self.name = "Planner"
        self.llm_client = llm_client
        self.instruction_prompt = instruction_prompt

    def plan(self, input_text: str):
        planner_prompt = self.instruction_prompt.format(question=input_text)

        messages: list[ChatMessage] = [{"role": "user", "content": planner_prompt}]

        response = self.llm_client.invoke(messages=messages)

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
        instruction_prompt: str,
    ):
        self.name = "executor"
        self.llm_client = llm_client
        self.instruction_prompt = instruction_prompt

    def execute(
        self,
        input_text: str,
        plan: list[str],
    ):

        history = []
        final_answer = ""
        for idx, item in enumerate(plan, start=1):
            print(f"🏃‍♀️ 正在执行计划第{idx}项：{item}")

            executor_prompt = self.instruction_prompt.format(
                question=input_text,
                plan=plan,
                history=history or "无",
                current_step=idx,
            )

            messages: list[ChatMessage] = [{"role": "user", "content": executor_prompt}]

            response = self.llm_client.invoke(messages=messages)
            history.append(f"步骤 {idx}：{item}\n结果：{response}")
            final_answer = response

        return final_answer


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
            planner_prompt = custom_prompts.get("planner", DEFAULT_PLANNER_PROMPT)
            executor_prompt = custom_prompts.get("executor", DEFAULT_PLANNER_PROMPT)
        else:
            planner_prompt = DEFAULT_PLANNER_PROMPT
            executor_prompt = DEFAULT_EXECUTOR_PROMPT

        self.planner = Planner(llm_client=self.llm, instruction_prompt=planner_prompt)
        self.executor = Executor(
            llm_client=self.llm, instruction_prompt=executor_prompt
        )

    def run(self, input_text: str, **kwargs) -> str:
        print(f"🤖 {self.name} 开始处理问题：{input}")

        plan = self.planner.plan(input_text=input_text)

        if not plan:
            final_answer = "无法生成有效的行动任务，任务终止。"
            print("\n--- ❌ 任务终止 ---\n")

            self.add_message(Message(role="user", content=input_text))
            self.add_message(Message(role="assistant", content=final_answer))

            return final_answer

        final_answer = self.executor.execute(input_text=input_text, plan=plan)
        print("--- ✅ 任务完成 ---")
        print(f"最终答案：{final_answer}")

        self.add_message(Message(role="user", content=input_text))
        self.add_message(Message(role="assistant", content=final_answer))

        return final_answer
