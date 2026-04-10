from core import Agent, CCAgentsLLM, Config, Message

DEFAULT_THOUGHT_PROMPT = """
请根据以下要求完成任务：

任务: {task}

请提供一个完整、准确的回答。
"""
DEFAULT_REFLECTION_PROMPT = """
请仔细审查以下回答，并找出可能的问题或改进空间：

# 原始任务:
{task}

# 当前回答:
{content}

请分析这个回答的质量，指出不足之处，并提出具体的改进建议。
如果回答已经很好，请回答"无需改进"。
"""
DEFAULT_REFINE_PROMPT = """
请根据反馈意见改进你的回答：

# 原始任务:
{task}

# 上一轮回答:
{last_attempt}

# 反馈意见:
{feedback}

请提供一个改进后的回答。
"""


class ReflectionAgent(Agent):
    def __init__(
        self,
        name: str,
        llm: CCAgentsLLM,
        system_prompt: str | None = None,
        config: Config | None = None,
        max_round: int = 3,
    ):
        super().__init__(name, llm, system_prompt, config)
        self.max_round = max_round

        self._memory = []

    def run(self, input_text: str, **kwargs) -> str:

        print(f"\n🤖 {self.name} 开始处理任务：{input_text}")

        print("\n--- 正在进行初次尝试 ---")
        initial_prompt = DEFAULT_THOUGHT_PROMPT.format(task=input_text)

        initial_thought_result = self.llm.invoke(
            [{"role": "user", "content": initial_prompt}]
        )

        cur_round = 0
        last_round_thought_result = initial_thought_result

        while cur_round < self.max_round:
            cur_round += 1

            print(f"\n--- 正在进行{cur_round}/{self.max_round}轮迭代 ---")

            print("\n->正在进行反思...")
            reflection_prompt = DEFAULT_REFLECTION_PROMPT.format(
                task=input_text, content=last_round_thought_result
            )

            feedback_response = self.llm.invoke(
                [{"role": "user", "content": reflection_prompt}]
            )

            if (
                "无需改进" in feedback_response
                or "no need for improvement" in feedback_response
            ):
                print("\n✅ 反思认为结果无需改进，任务完成")
                break

            print("\n-> 正在进行优化...")
            refine_prompt = DEFAULT_REFINE_PROMPT.format(
                task=input_text,
                last_attempt=last_round_thought_result,
                feedback=feedback_response,
            )

            refined_result = self.llm.invoke(
                [{"role": "user", "content": refine_prompt}]
            )

            last_round_thought_result = refined_result

        print(f"\n--- 任务完成 ---\n最终结果：\n{last_round_thought_result}")

        self.add_message(Message(role="user", content=input_text))
        self.add_message(Message(role="assistant", content=last_round_thought_result))

        return last_round_thought_result
