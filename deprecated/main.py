import argparse
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from prompts import SYSTEM_MESSAGE
from tools *

TOOL_CALL_PATTERN = re.compile(r"<\|tool_call\|>(.*?)<\|tool_call\|>", re.DOTALL)
ANSWER_PATTERN = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)
OPENROUTER_URL: str = "https://openrouter.ai/api/v1"
DOTENV_PATH = Path(__file__).with_name(".env")
MAX_ITERS: int = 10000
# MODEL_NAME: str = "google/gemma-4-26b-a4b-it:free"
# MODEL_NAME: str = "liquid/lfm-2.5-1.2b-thinking:free"
# MODEL_NAME: str = "nvidia/nemotron-3-super-120b-a12b:free"
# MODEL_NAME: str = "z-ai/glm-4.5-air:free"
# MODEL_NAME: str = "nousresearch/hermes-3-llama-3.1-405b:free"

# MODEL_NAME: str = "openai/gpt-oss-120b:free"
MODEL_NAME: str = "nvidia/nemotron-3-super-120b-a12b:free"

load_dotenv(DOTENV_PATH)


def _get_openrouter_api_key() -> str:
    """Return the API key required to talk to OpenRouter."""

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key

    msg = (
        f"Missing OPENROUTER_API_KEY. Set it in {DOTENV_PATH} "
        "or export it in the current shell."
    )
    raise SystemExit(msg)


def main(user_message: str) -> None:
    """Send a user message to the model and print the response."""

    api_key = _get_openrouter_api_key()

    try:
        client = OpenAI(
            base_url=OPENROUTER_URL,
            api_key=api_key,
        )

        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_message},
        ]
        completion = client.chat.completions.create(model=MODEL_NAME, messages=messages)
        response = completion.choices[0].message.content or ""
        print("Completion: ", response)
    except OpenAIError as exc:
        msg = f"OpenRouter request failed: {exc}"
        raise SystemExit(msg) from exc

    tool_match = TOOL_CALL_PATTERN.search(response)
    if tool_match:
        tool_call = json.loads(tool_match.group(1).strip())
    else:
        tool_call = ""

    answer_match = ANSWER_PATTERN.search(response)
    if answer_match:
        answer = answer_match.group(1).strip()
    else:
        answer = ""

    print("Answer: ", answer)
    if tool_call:
        func = getattr(file_search, tool_call["name"])
        args = tool_call["args"]
        print(func, args)

        res = func(**args)
        print("Tool call result: ", res)
        messages.append({"role": "assistant", "content": response})
        messages.append(
            {
                "role": "user",
                "content": f"Here's the tool call result: <|tool_call_result|> {res} <|tool_call_result|>",
            }
        )
        new_agent = client.chat.completions.create(model=MODEL_NAME, messages=messages)
        print(new_agent.choices[0].message.content)


def parse_tool_call_result():
    pass


def parse_answer_tags():
    pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Hi", type=str)

    args = parser.parse_args()
    main(args.prompt)
