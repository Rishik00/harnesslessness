import argparse
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from config import Answer, ToolCallResult
from prompts import SYSTEM_MESSAGE
from tools import file_search as file_search

TOOL_CALL_PATTERN = re.compile(r"<\|tool_call\|>(.*?)<\|tool_call\|>", re.DOTALL)
ANSWER_PATTERN = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)
OPENROUTER_URL: str = "https://openrouter.ai/api/v1"
DOTENV_PATH = Path(__file__).with_name(".env")
MAX_ITERS: int = 10000
MODEL_NAME: str = "nvidia/nemotron-3-super-120b-a12b:free"

load_dotenv(DOTENV_PATH)


def parse_result(response: str) -> ToolCallResult | Answer:
    """Parse a raw model response into a ToolCallResult or Answer."""
    tool_match = TOOL_CALL_PATTERN.search(response)

    if tool_match:
        tool_call = json.loads(tool_match.group(1).strip())
        return ToolCallResult(
            function_name=tool_call["name"],
            args=tool_call.get("args", {}),
        )

    answer_match = ANSWER_PATTERN.search(response)
    if answer_match:
        answer = answer_match.group(1).strip()
        return Answer(final_answer=answer)

    msg = "Response did not contain a tool call or answer tag."
    raise ValueError(msg)


def _get_openrouter_key() -> str:
    """Return the OpenRouter API key from the environment, or exit with an error."""
    api_key: str | None = os.environ.get("OPENROUTER_API_KEY")

    if api_key:
        return api_key

    msg = (
        f"Missing OPENROUTER_API_KEY. Set it in {DOTENV_PATH} "
        "or export it in the current shell."
    )
    raise SystemExit(msg)


def run(prompt: str) -> None:
    """Run the agent loop for a given prompt, printing the final answer."""
    api_key = _get_openrouter_key()

    client = OpenAI(
        base_url=OPENROUTER_URL,
        api_key=api_key,
    )

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": prompt},
    ]

    iter = 0
    while True:
        # TBD: if we're at max iters tell the model with one more turn and summarize the
        # conversation
        if iter >= MAX_ITERS:
            print("Max iters reached!")
            break

        completion = client.chat.completions.create(model=MODEL_NAME, messages=messages)
        response = completion.choices[0].message.content or ""
        parse = parse_result(response)
        messages.append({"role": "assistant", "content": response})

        if isinstance(parse, ToolCallResult):
            func = getattr(file_search, parse.function_name)
            result = func(**parse.args)
            messages.append(
                {
                    "role": "user",
                    "content": f"Here's the tool call result: <|tool_call_result|> {result} <|tool_call_result|>",
                }
            )
        else:
            print("Final answer: ", parse.final_answer)
            break

        iter += 1

    print(f"Taken {iter} iters to finish the thing.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Hi, what are you?")
    args = parser.parse_args()

    run(args.prompt)
