# cleaner_deepagents

A minimal agentic loop that connects an LLM (via OpenRouter) to file-search tools. The agent reasons, calls tools, observes results, and repeats until it can give a verified final answer

## Quickstart

**1. Install dependencies**
```
pip install openai python-dotenv
```

**2. Set your API key**

Create a `.env` file next to `loop.py`:
```
OPENROUTER_API_KEY=sk-or-...
```

**3. Run**
```
python loop.py --prompt "what files are in the current directory?"
```

## How it works

```
loop.py          — agent loop: calls model, dispatches tools, iterates until <answer>
config.py        — ToolCallResult and Answer dataclasses
prompts.py       — builds SYSTEM_MESSAGE from tool schemas
tools/
  file_search.py — ls_tool, read_tool and their schemas
```

Each turn the model either emits a `<|tool_call|>` block (tool is executed, result fed back) or an `<answer>` block (loop exits). `MAX_ITERS` in `loop.py` caps runaway loops.

## Adding a tool

1. Define the function and its `_schema` dict in `tools/file_search.py`.
2. Add both to `__all__`.
3. Add the schema to the `_SCHEMAS` list in `prompts.py`.
