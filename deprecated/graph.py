# Deepagents has 2 main things going for it:
# backends: there for file execution calls
# middleware: there for agent behaviour, access.
# create_deep_agent() is the main entry point that returns a compiled state graph


# I never thought of writing something like this, but here I have to anyway.
# change of plans: I want to make a minimal version of the current deepagents and see what happens
# It's a point of entry:
# create_new_agent that takes a bunch of tools.

import json
import os
import re
import subprocess
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

import requests

import tools.file_search as file_search

tool_descriptions = {
    "hello_world_tool": f"{file_search.hello_world_tool.__doc__}",
    "ls_tool": f"{file_search.ls_tool.__doc__}
}

SYSTEM_MESSAGE = f"""
You are spinx, an ai agent. Your job is to answer user questions accurately.

## Tools
You have access to the following tools:
{chr(10).join(f"- {name}: {desc}" for name, desc in tool_descriptions.items())}

## Tool Calling
If you need to call a tool, respond with:
<tool_call>{{"name": "tool_name", "args": {{"arg1": "value1"}}</tool_call>

IMPORTANT: If you find that the function has no arguments, you don't have to add any arguments in the tool call.

You will then receive the result as:
<tool_call_result>result here</tool_call_result>

VERY IMPORTANT:
Do NOT include any other text in the same response as a tool call.
Do NOT assume or predict what the tool will return.
Do NOT write the answer until you have received the <tool_call_result>.
Wait for the result before continuing.

## Final Answer
When you have enough information, respond with:
<answer>your final answer here</answer>
"""


MODEL_NAME: str = "openai/gpt-oss-120b:free"
OPENROUTER_URL: str = "https://openrouter.ai/api/v1"
USER_MESSAGE = "Do 2 things: tell me about yourself and also use the hello world tool."

client = OpenAI(
    base_url=OPENROUTER_URL,
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)
messages = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    {"role": "user", "content": USER_MESSAGE},
]
completion = client.chat.completions.create(model=MODEL_NAME, messages=messages)
response = completion.choices[0].message.content
TOOL_CALL_PATTERN = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)
ANSWER_PATTERN = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)

tool_match = TOOL_CALL_PATTERN.search(response)
if tool_match:
    tool_call = json.loads(tool_match.group(1).strip())
else:
    tool_call = ""

answer_match = ANSWER_PATTERN.search(response)
# print(answer_match)
if answer_match:
    answer = answer_match.group(1).strip()
else:
    answer = ""

print("Tool call: ", tool_call)
print("Answer: ", answer)

if tool_call:
    func = getattr(file_search, tool_call["name"])
    res = func()
    print("Tool call result: ", res)
    messages.append({"role": "assistant", "content": response})
    messages.append(
        {
            "role": "user",
            "content": f"Here's the tool call result: <tool_call_result> {res} </tool_call_result>",
        }
    )
    new_agent = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    print(new_agent.choices[0].message.content)


def new_agent(model_str: str, tools: List[str]):
    pass
