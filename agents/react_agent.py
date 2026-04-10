import re

from core import Agent, CCAgentsLLM, Config, Message
from tools import ToolRegistry

DEFAULT_REACT_PROMPT = """
你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤：

**Thought:** 分析当前问题，思考需要什么信息或采取什么行动。
**Action:** 选择一个行动，格式必须是以下之一：
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循：工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动："""


class ReActAgent(Agent):
    def __init__(
        self,
        name: str,
        llm: CCAgentsLLM,
        tool_registry: ToolRegistry,
        system_prompt: str | None = None,
        config: Config | None = None,
        max_steps: int = 5,
        custom_prompt: str | None = None,
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.prompt_template = custom_prompt or DEFAULT_REACT_PROMPT

        # 记录模型执行过程中输出的内容
        self._in_process_history = []

    def run(self, input_text: str, max_steps: int = 3, **kwargs) -> str:

        # 每次运行前都清空
        self._in_process_history = []

        print(f"\n🤖 {self.name} 开始执行")
        final_steps = max_steps or self.max_steps
        cur_step = 0

        while cur_step < final_steps:
            cur_step += 1
            print(f"\n--- 🏃‍♀️ 第{cur_step} 步 ---")

            tool_prompt = self.tool_registry.get_tools_description()
            history_str = "\n".join(self._in_process_history)
            prompt = self.prompt_template.format(
                tools=tool_prompt,
                question=input_text,
                history=history_str,
            )

            # 调用 LLM
            response_text = self.llm.invoke([{"role": "user", "content": prompt}])

            thought, action = self._parse_output(response_text)

            if thought:
                print(f"🤔 思考：{thought}")

            if not action:
                print("⚠️ 警告：未解析出有效的 action，流程终止")
                break

            if action.startswith("Finish"):
                final_answer = self._parse_answer(action)
                print(f"🎉 最终答案：{final_answer}")

                self.add_message(Message(role="user", content=prompt))
                self.add_message(Message(role="assistant", content=final_answer))

                return final_answer

            tool_name, tool_input = self._parse_action(action)

            if not tool_name or tool_input is None:
                self._in_process_history.append(
                    "Action Result: 无效的action格式，请检查！"
                )
                continue

            print(f"行动：{tool_name}[{tool_input}]")

            action_result = self.tool_registry.execute_tool(tool_name, tool_input)
            print(f"👀 第{cur_step}步调用工具的结果为{action_result}")

            self._in_process_history.append(f"Action: {action}")
            self._in_process_history.append(f"Action Result: {action_result}")

        print("⏰ 已经达到最大步数，流程终止！")
        final_answer = "抱歉，无法在规定的步数内完成这个任务"

        self.add_message(Message(role="user", content=input_text))
        self.add_message(Message(role="assistant", content=final_answer))

        return final_answer

    def _parse_action(self, text: str):
        match = re.match(r"(\w+)\[(.*)\]", text)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _parse_answer(self, text: str):
        answer_match = re.match(r"\w+\[(.*)\]", text)
        return answer_match.group(0).strip() if answer_match else ""

    def _parse_output(self, text: str):
        thought_match = re.search(r"Thought:(.*)", text)
        action_match = re.search(r"Action:(.*)", text)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action
