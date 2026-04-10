from typing import Any, Callable

from .base import Tool


class ToolRegistry:
    """
    工具注册表

    提供工的注册，管理和执行

    支持两种工具的注册：
    - Tool 对象注册（推荐）
    - 函数直接注册（简单）
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def registry_tool(self, tool: Tool):
        if tool.name in self._tools:
            print(f"⚠️ 工具 [{tool.name}] 已存在，将被覆盖")

        self._tools[tool.name] = tool
        print(f"✅ 工具 [{tool.name}] 注册成功！")

    def registry_function(
        self, name: str, description: str, func: Callable[[str], str]
    ):
        if name in self._functions:
            print(f"⚠️ 简单工具 [{name}] 已存在，将被覆盖")

        self._functions[name] = {
            "name": name,
            "description": description,
            "func": func,
        }

        print(f"✅ 简单工具 [{name}] 注册成功！")

    def unregister(self, name):
        if name in self._tools:
            del self._tools[name]
            print(f"🗑 工具 [{name}] 已注销")

        elif name in self._functions:
            del self._functions[name]
            print(f"🗑 简单工具 [{name}] 已注销")
        else:
            print(f"⚠️ 工具 [{name}] 不存在")

    def get_tool(self, name):
        return self._tools.get(name)

    def get_function(self, name):
        func_info = self._functions.get(name)
        return func_info["func"] if func_info else None

    # todo: 这个真的有必要吗
    def execute_tool(self, name, input_text: str):
        if name in self._tools:
            tool = self._tools["name"]
            try:
                return tool.run({"input": input_text})
            except Exception as e:
                return f"❌ 执行工具 [{name}] 时发生异常:{e}"
        elif name in self._functions:
            func_info = self._functions["name"]
            try:
                return func_info["func"](input_text)
            except Exception as e:
                return f"❌ 执行简单工具 [{name}] 时发生异常:{e}"
        else:
            return f"❌ 未找到名为 [{name}] 的工具"

    def get_tools_description(self):
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        for func_info in self._functions.values():
            descriptions.append(f"- {func_info['name']}: {func_info['description']}")

        return "\n".join(descriptions)

    def list_tools(self):
        return list(self._tools.keys()) + list(self._functions.keys())

    def get_all_tools(self):
        return list(self._tools.values())

    def get_all_functions(self):
        return list(self._functions.values())

    def clear(self):
        self._tools.clear()
        self._functions.clear()
        print("🧹 所有工具已清空")
