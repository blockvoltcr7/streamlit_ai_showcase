from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

def add(a: float, b: float) -> float:
  """Add two numbers and returns the result"""
  return a + b
add_tool = FunctionTool.from_defaults(fn=add)

def multiply(a: float, b: float) -> float:
  """Multiply two numbers and returns the result"""
  return a * b
multiply_tool = FunctionTool.from_defaults(fn=multiply)

def subtract(a: float, b: float) -> float:
  """Subtract two numbers and returns the result"""
  return a - b
subtract_tool = FunctionTool.from_defaults(fn=subtract)

def divide(a: float, b: float) -> float:
  """Divide two numbers and returns the result. Handles division by zero error"""
  if b == 0:
    raise ZeroDivisionError("Division by zero is not allowed")
  return a / b
divide_tool = FunctionTool.from_defaults(fn=divide)

# Scientific functions
def power(a: float, b: float) -> float:
  """Raise a number to a power and returns the result"""
  return a ** b
power_tool = FunctionTool.from_defaults(fn=power)

def factorial(n: int) -> int:
  """Calculate the factorial of a non-negative integer and returns the result"""
  if n < 0:
    raise ValueError("Factorial is not defined for negative numbers")
  if n == 0:
    return 1
  else:
    return n * factorial(n-1)
factorial_tool = FunctionTool.from_defaults(fn=factorial)

def sine(x: float) -> float:
  """Calculate the sine of an angle in radians and returns the result. Uses the math library"""
  import math
  return math.sin(x)
sine_tool = FunctionTool.from_defaults(fn=sine)

def cosine(x: float) -> float:
  """Calculate the cosine of an angle in radians and returns the result. Uses the math library"""
  import math
  return math.cos(x)
cosine_tool = FunctionTool.from_defaults(fn=cosine)

def tangent(x: float) -> float:
  """Calculate the tangent of an angle in radians and returns the result. Handles division by zero error"""
  if cosine(x) == 0:
    raise ZeroDivisionError("Tangent is not defined for angles where cosine is zero")
  return sine(x) / cosine(x)
tangent_tool = FunctionTool.from_defaults(fn=tangent)

# list of tools

tools = [multiply_tool, add_tool, subtract_tool, divide_tool, power_tool, factorial_tool, sine_tool, cosine_tool, tangent_tool]

llm = OpenAI(model="gpt-3.5-turbo")
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)

response = agent.chat("What is 20+(2*4)? Calculate step by step ")
print(response)
response = agent.query("Calculate cos(30) + tan(45)")
print(response)
