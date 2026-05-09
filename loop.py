import argparse
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from rich.live import Live

import tools

# Local imports
from config import Answer, ToolCallResult
from demo_rich import build_layout
from prompts import SYSTEM_MESSAGE

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


def _extract_reasoning(response: str) -> str | None:
    """Return any text before the first tool-call or answer tag, if non-empty."""
    tool_idx = response.find("<|tool_call|>")
    answer_idx = response.find("<answer>")
    cut = min(
        tool_idx if tool_idx >= 0 else len(response),
        answer_idx if answer_idx >= 0 else len(response),
    )
    reasoning = response[:cut].strip()
    return reasoning or None


def run(prompt: str) -> None:
    """Run the agent loop for a given prompt with a live Rich UI."""
    api_key = _get_openrouter_key()

    client = OpenAI(
        base_url=OPENROUTER_URL,
        api_key=api_key,
    )

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": prompt},
    ]

    events: list[dict] = []
    iter_count = 0
    done = False
    final_answer = ""

    with Live(
        build_layout(prompt, events, iter_count, done, MODEL_NAME),
        refresh_per_second=10,
        screen=True,
    ) as live:
        for _ in range(MAX_ITERS):
            events.append({"type": "waiting"})
            live.update(build_layout(prompt, events, iter_count, done, MODEL_NAME))

            completion = client.chat.completions.create(
                model=MODEL_NAME, messages=messages
            )
            events.pop()  # remove waiting indicator
            response = completion.choices[0].message.content or ""

            parse = parse_result(response)
            messages.append({"role": "assistant", "content": response})

            reasoning = _extract_reasoning(response)
            if reasoning:
                events.append({"type": "think", "content": reasoning})
                live.update(build_layout(prompt, events, iter_count, done, MODEL_NAME))

            if isinstance(parse, ToolCallResult):
                events.append(
                    {
                        "type": "tool_call",
                        "name": parse.function_name,
                        "args": json.dumps(parse.args),
                    }
                )
                live.update(build_layout(prompt, events, iter_count, done, MODEL_NAME))

                func = getattr(tools, parse.function_name)
                result = func(**parse.args)

                events.append({"type": "tool_result", "content": str(result)})
                iter_count += 1
                live.update(build_layout(prompt, events, iter_count, done, MODEL_NAME))

                messages.append(
                    {
                        "role": "user",
                        "content": f"Here's the tool call result: <|tool_call_result|> {result} <|tool_call_result|>",
                    }
                )
            else:
                final_answer = parse.final_answer
                events.append({"type": "answer", "content": final_answer})
                done = True
                live.update(build_layout(prompt, events, iter_count, done, MODEL_NAME))
                time.sleep(3)
                break
        else:
            live.update(build_layout(prompt, events, iter_count, done, MODEL_NAME))
            time.sleep(2)

    if final_answer:
        print("Final answer:", final_answer)
    print(f"Taken {iter_count} iters.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Hi, what are you?")
    args = parser.parse_args()

    run(args.prompt)
