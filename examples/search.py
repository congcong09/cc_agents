from tools.builtin.search import SearchTool

SERPAPI_API_KEY = "bd04836c259cbdd827931dac84b8df735e59a6e71aea4973d8ce046989a42f41"
TAVILY_API_KEY = "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"

search = SearchTool(serpapi_key=SERPAPI_API_KEY, tavily_key=TAVILY_API_KEY)

result = search.run({"query": "美伊和谈进展"})

print(result)
