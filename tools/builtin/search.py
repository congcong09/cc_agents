import os
from typing import Any, Literal

from tools.base import Tool, ToolParameter

AVAILABLE_BACKEND = Literal["hybrid", "tavily", "serpapi"]


class SearchTool(Tool):
    def __init__(
        self,
        *,
        backend: AVAILABLE_BACKEND = "hybrid",
        tavily_key: str | None = None,
        serpapi_key: str | None = None,
    ):
        super().__init__(
            "search",
            "一个智能网页搜索引擎。支持混合搜索模式，自动选择最佳搜索源。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。",
            [
                ToolParameter(
                    name="query",
                    description="要搜索的内容",
                    type="string",
                )
            ],
        )

        self.backend = backend
        self.tavily_key = tavily_key or os.getenv("TAVILY_API_KEY")
        self.serpapi_key = serpapi_key or os.getenv("SERPAPI_API_KEY")
        self.available_backends = []
        self._setup_backend()

    def _setup_backend(self):
        """配置搜索后端"""
        if self.tavily_key:
            try:
                from tavily import TavilyClient

                self.tavily_clint = TavilyClient(api_key=self.tavily_key)
                self.available_backends.append("tavily")
                print("✅ Tavily 搜索引擎已初始化")
            except ImportError:
                print("❌ Tavily 未安装，无法使用Tavily搜索")
        else:
            print("❌ TAVILY_API_KEY 未设置，无法使用 Tavily 功能")

        if self.serpapi_key:
            try:
                import serpapi

                self.serpapi_client = serpapi.Client(api_key=self.serpapi_key)
                self.available_backends.append("serpapi")
                print("✅ SerpApi 搜索引擎已初始化")
            except ImportError:
                print("❌ SerpApi 未安装，无法使用 SerpApi 搜索")
        else:
            print("❌ SERPAPI_API_KEY 未设置，无法使用 Serpapi 功能")

        if self.backend == "hybrid":
            if self.available_backends:
                print(
                    f"🔧 混合搜索模式已启用，可用后端: {', '.join(self.available_backends)}"
                )
            else:
                print("⚠️ 没有可用的搜索后端，请配置API密钥")
        elif self.backend == "tavily" and "tavily" not in self.available_backends:
            print("⚠️ Tavily不可用，请检查TAVILY_API_KEY配置")
        elif self.backend == "serpapi" and "serpapi" not in self.available_backends:
            print("⚠️ SerpApi不可用，请检查SERPAPI_API_KEY配置")
        elif self.backend not in ["tavily", "serpapi", "hybrid"]:
            print("⚠️ 不支持的搜索后端，将使用hybrid模式")
            self.backend = "hybrid"

    def run(self, parameters: dict[str, Any]) -> str:
        query = parameters.get("query", "").strip()
        if not query:
            return "❌ 搜索内容不能为空"
        print(f"🔍 正在执行搜索：{query}")

        if self.backend == "hybrid":
            return self._search_hybrid(query)
        elif self.backend == "tavily":
            return self._search_tavily(query)
        elif self.backend == "serpapi":
            return self._search_serpapi(query)
        else:
            return self._get_api_config_message()

    def _search_hybrid(self, query: str) -> str:
        """混合搜索 - 智能选择最佳搜索源"""
        if not self.available_backends:
            return self._get_api_config_message()

        if "tavily" in self.available_backends:
            try:
                print("🎯 使用 Tavily 进行AI优化搜索")
                return self._search_tavily(query=query)
            except Exception as e:
                print(f"⚠️ 使用 Tavily 搜索失败：{e}")

        if "serpapi" in self.available_backends:
            try:
                print("🎯 使用 Serpapi 进行Google搜索")
                return self._search_serpapi(query=query)
            except Exception as e:
                print(f"⚠️ 使用 Serpapi 搜索失败：{e}")

        return "❌ 搜索失败，请检查网络连接和API配置"

    def _search_tavily(self, query: str) -> str:
        """使用 tavily 搜索"""
        response = self.tavily_clint.search(
            query=query,
            search_depth="basic",
            include_answer=True,
            max_results=3,
        )

        result = f"🎯 Tavily AI搜索结果：{response.get('answer', '未找到直接答案')}\n\n"

        for i, item in enumerate(response.get("results", [])[:3], 1):
            result += f"[{i}] {item.get('title')}\n"
            result += f"  {item.get('content', '')[:200]}...\n"
            result += f"  来源：{item.get('url', '')}\n\n"

        return result

    def _search_serpapi(self, query: str) -> str:
        """使用serpapi搜索"""
        response = self.serpapi_client.search(
            {
                "engine": "google",
                "q": query,
                "gl": "cn",
                "hl": "zh-cn",
            }
        )

        response_data = response.as_dict()

        result_text = ""
        result = "Serpapi google搜索结果：\n\n"

        if "answer_box" in response_data and "answer" in response_data["answer_box"]:
            result += f"💡 直接答案：{response_data['answer_box']['answer']}\n\n"
            result_text = result

        if (
            "knowledge_graph" in response_data
            and "description" in response_data["knowledge_graph"]
        ):
            result += (
                f"📚 知识图谱：{response_data['knowledge_graph']['description']}\n\n"
            )
            result_text = result

        if "organic_results" in response_data and response_data["organic_results"]:
            result += "🔗 相关结果：\n"
            for i, res in enumerate(response_data["organic_results"], 1):
                result += f"[{i}] {res.get('title', '')}\n"
                result += f"  {res.get('snippet', '')}\n"
                result += f"  来源：{res.get('link', '')}\n\n"
            result_text = result

        return result_text or f"没有找到关于 [{query}] 的信息"

    def _get_api_config_message(self) -> str:
        """获取API配置提示信息"""
        tavily_key = os.getenv("TAVILY_API_KEY")
        serpapi_key = os.getenv("SERPAPI_API_KEY")

        message = "❌ 没有可用的搜索源，请检查以下配置：\n\n"

        # 检查Tavily
        message += "1. Tavily API:\n"
        if not tavily_key:
            message += "   ❌ 环境变量 TAVILY_API_KEY 未设置\n"
            message += "   📝 获取地址: https://tavily.com/\n"
        else:
            try:
                import tavily

                message += "   ✅ API密钥已配置，包已安装\n"
            except ImportError:
                message += (
                    "   ❌ API密钥已配置，但需要安装包: pip install tavily-python\n"
                )

        message += "\n"

        # 检查SerpAPI
        message += "2. SerpAPI:\n"
        if not serpapi_key:
            message += "   ❌ 环境变量 SERPAPI_API_KEY 未设置\n"
            message += "   📝 获取地址: https://serpapi.com/\n"
        else:
            try:
                import serpapi

                message += "   ✅ API密钥已配置，包已安装\n"
            except ImportError:
                message += "   ❌ API密钥已配置，但需要安装包: pip install google-search-results\n"

        message += "\n配置方法：\n"
        message += "- 在.env文件中添加: TAVILY_API_KEY=your_key_here\n"
        message += "- 或在环境变量中设置: export TAVILY_API_KEY=your_key_here\n"
        message += "\n配置后重新运行程序。"

        return message
