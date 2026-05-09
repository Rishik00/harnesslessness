from dataclasses import dataclass


@dataclass
class ToolCallResult:
    args: dict | None
    function_name: str


@dataclass
class Answer:
    final_answer: str = "Hello world"
