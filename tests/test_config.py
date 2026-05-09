from config import Answer, ToolCallResult


def test_configs() -> None:
    dummy_tool_call = {
        "function_name": "file_search",
        "args": {
            "query": "find the nearest library",
            "top_k": 3,
        },
    }
    dummy_answer = {
        "final_answer": "Use the downtown branch.",
    }

    tool_call = ToolCallResult(**dummy_tool_call)
    answer = Answer(**dummy_answer)

    assert isinstance(tool_call, ToolCallResult)
    assert isinstance(tool_call.function_name, str)
    assert isinstance(tool_call.args, dict)
    assert isinstance(answer, Answer)
    assert isinstance(answer.final_answer, str)
