"""
Rich demo — run with: python demos/demo_rich.py

Framework: Rich  (pip install rich)
Approach:  Live-updating layout. No widgets, no event loop —
           just panels that redraw as the agent "runs".
"""

import time
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.padding import Padding

console = Console()

PROMPT = "What Python files exist in this project, and what does loop.py do?"

SCRIPT = [
    {
        "type": "think",
        "content": (
            "The user wants to know what Python files exist and what loop.py does.\n"
            "I have no prior knowledge of this environment.\n"
            "Step 1: call ls_tool to list the directory.\n"
            "Step 2: once I have the list, call read_tool on loop.py."
        ),
    },
    {
        "type": "tool_call",
        "name": "ls_tool",
        "args": '{"dir": "."}',
    },
    {
        "type": "tool_result",
        "content": "['loop.py', 'config.py', 'prompts.py', 'utils.py', 'tools/', 'tests/', 'deprecated/']",
    },
    {
        "type": "think",
        "content": (
            "I can see the directory listing. Python files are:\n"
            "  loop.py, config.py, prompts.py, utils.py\n"
            "Now I need to read loop.py to describe what it does."
        ),
    },
    {
        "type": "tool_call",
        "name": "read_tool",
        "args": '{"file_path": "loop.py"}',
    },
    {
        "type": "tool_result",
        "content": (
            "import argparse, json, os, re ...\n"
            "TOOL_CALL_PATTERN = re.compile(...)\n"
            "def parse_result(response): ...\n"
            "def run(prompt): ...  # agent loop\n"
            "if __name__ == '__main__': ..."
        ),
    },
    {
        "type": "think",
        "content": (
            "I have enough to answer. loop.py is the main agent loop:\n"
            "it calls the model, parses tool calls or answers,\n"
            "dispatches tool functions, and iterates until <answer>."
        ),
    },
    {
        "type": "answer",
        "content": (
            "Python files in the project: loop.py, config.py, prompts.py, utils.py.\n\n"
            "loop.py is the agent harness — it runs a while-loop that calls the LLM,\n"
            "parses the response for either a <|tool_call|> or <answer> tag,\n"
            "executes tool functions when needed, and breaks when the model\n"
            "produces a final answer."
        ),
    },
]


def _header(prompt: str) -> Panel:
    title = Text("SPHINX", style="bold white", justify="center")
    sub = Text(f'"{prompt}"', style="italic dim", justify="center")
    return Panel(
        Padding(Text.assemble(title, "\n", sub), (0, 2)),
        style="bold blue",
        box=box.HEAVY,
    )


_MAX_RESULT_LINES = 6


def _event_panel(events: list[dict]) -> Panel:
    # Keep only as many recent events as fit; header=5, status=3, borders≈4
    available = max(console.size.height - 12, 6)

    def _cost(ev: dict) -> int:
        if ev["type"] == "think":
            return len(ev["content"].splitlines()) + 2
        if ev["type"] == "tool_result":
            return min(len(ev["content"].splitlines()), _MAX_RESULT_LINES) + 3
        if ev["type"] == "waiting":
            return 2
        return 3  # tool_call / answer

    total, cutoff = 0, len(events)
    for i in range(len(events) - 1, -1, -1):
        total += _cost(events[i])
        if total > available:
            cutoff = i + 1
            break
    else:
        cutoff = 0

    lines = Text()
    if cutoff:
        lines.append(f"  ··· {cutoff} earlier event(s) ···\n\n", style="dim italic")

    for ev in events[cutoff:]:
        if ev["type"] == "think":
            lines.append("◆ Reasoning\n", style="bold yellow")
            for line in ev["content"].splitlines():
                lines.append(f"  {line}\n", style="yellow")
        elif ev["type"] == "tool_call":
            lines.append(f"⚙  Tool call → {ev['name']}\n", style="bold cyan")
            lines.append(f"  args: {ev['args']}\n", style="cyan")
        elif ev["type"] == "tool_result":
            lines.append("✔  Result\n", style="bold green")
            content_lines = ev["content"].splitlines()
            for line in content_lines[:_MAX_RESULT_LINES]:
                lines.append(f"  {line}\n", style="green")
            if len(content_lines) > _MAX_RESULT_LINES:
                lines.append(f"  … {len(content_lines) - _MAX_RESULT_LINES} more line(s) …\n", style="dim green")
        elif ev["type"] == "answer":
            lines.append("─" * 40 + "\n", style="bold magenta")
            lines.append("  Final Answer\n", style="bold magenta")
            lines.append("─" * 40 + "\n", style="bold magenta")
            lines.append(ev["content"], style="bold white")
            lines.append("\n")
        elif ev["type"] == "waiting":
            lines.append("  ⟳ awaiting model…\n", style="dim white")
        lines.append("\n")
    return Panel(lines, title="[bold]Trace[/bold]", box=box.ROUNDED, border_style="dim white")


def _status_panel(iter_count: int, done: bool, model: str = "nvidia/nemotron-3-super-120b") -> Panel:
    if done:
        status = Text("● done", style="bold green")
    else:
        status = Text("● running", style="bold yellow")
    body = Text.assemble(
        status,
        "   ",
        Text(f"iters: {iter_count}", style="dim"),
        "   ",
        Text(f"model: {model}", style="dim"),
    )
    return Panel(body, box=box.SIMPLE)


def build_layout(prompt: str, events: list[dict], iter_count: int, done: bool, model: str = "nvidia/nemotron-3-super-120b") -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(_header(prompt), name="header", size=5),
        Layout(_event_panel(events), name="trace"),
        Layout(_status_panel(iter_count, done, model), name="status", size=3),
    )
    return layout


def main():
    events: list[dict] = []
    iter_count = 0

    done = False
    live = Live(build_layout(PROMPT, events, iter_count, done), refresh_per_second=10, screen=True)
    with live:
        time.sleep(0.6)
        for step in SCRIPT:
            events.append(step)
            if step["type"] == "tool_result":
                iter_count += 1
            done = step["type"] == "answer"
            live.update(build_layout(PROMPT, events, iter_count, done))
            time.sleep(1.4 if step["type"] == "think" else 0.9)
        time.sleep(4)


if __name__ == "__main__":
    main()
