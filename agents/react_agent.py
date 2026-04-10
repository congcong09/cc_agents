from core import Agent, CCAgentsLLM, Config
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
    ):
        super().__init__(name, llm, system_prompt, config)
        self.max_steps = max_steps

    def run(self, input_text: str, max_steps: int = 3, **kwargs) -> str:
        history = []

        final_steps = max_steps or self.max_steps
        cur_step = 0

        while cur_step < final_steps:
            cur_step += 1
            prompt = DEFAULT_REACT_PROMPT.format(
                question=input_text, history=history or "无"
            )

            response_text = self.llm.invoke([{"role": "user", "content": prompt}])

            response_data = self._extract_data(response_text)

            if response_data.get("error"):
                error_msg = response_data.get("error")
                print(f"--- ❌ 执行失败 --- \n错误：{error_msg}")

            elif response_data.get("finish"):
                answer = response_data.get("finish")
                print(f"--- ✅ 执行成功 ---\n结果：{answer}")
                break

    def _extract_data(self, text: str) -> dict[str, str]:
        if "Thought" not in text or "Action" not in text:
            return {"error": "未找到有效的内容，终止任务"}

        return {}
