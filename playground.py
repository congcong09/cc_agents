import re

response_text = """

问题: {question}

请严格按照以下格式输出你的计划:
```json
["步骤1", "步骤2", "步骤3", ...]
```
"""

match = re.search(r"```json\s*(.*?)\s*```", response_text)
if match:
    plan_str = match.group(1).strip()
else:
    plan_str = "[]"

print(plan_str)
