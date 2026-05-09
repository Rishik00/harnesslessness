from dataclasses import dataclass


@dataclass
class ToolCallResult:
    """Parsed tool call extracted from a model response."""

    args: dict | None
    function_name: str


@dataclass
class Answer:
    """Final answer produced by the agent."""

    final_answer: str = "Hello world"
