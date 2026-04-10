from serpapi import Client

serpapi_client = Client(
    api_key="bd04836c259cbdd827931dac84b8df735e59a6e71aea4973d8ce046989a42f41"
)

response = serpapi_client.search(
    {
        "engine": "google",
        "q": "美国是什么时候独立的",
        "gl": "cn",
        "hl": "zh-cn",
    }
)

print(response)
