from tools.builtin.calculator import CalculatorTool

cal = CalculatorTool()

result = cal.run({"input": "2 + 2 * max(10, 1000)"})

print(result)
