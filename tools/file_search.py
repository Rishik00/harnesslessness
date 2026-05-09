import os

from .utils import verify_path_exists

ls_tool_schema = {
    "name": "ls_tool",
    "description": "Lists the files and folders inside a directory.",
    "args": {
        "dir": {
            "type": "str",
            "required": True,
            "description": "Absolute or relative path to the directory to list.",
        }
    },
}


def ls_tool(dir: str) -> list[str] | str:
    """List files and folders in a directory."""
    if not verify_path_exists(dir):
        return f"Error: path does not exist: {dir}"
    return os.listdir(dir)


read_tool_schema = {
    "name": "read_tool",
    "description": "Reads and returns the full text contents of a file.",
    "args": {
        "file_path": {
            "type": "str",
            "required": True,
            "description": "Absolute or relative path to the file to read.",
        }
    },
}


def read_tool(file_path: str) -> str:
    """Read and return the full text contents of a file."""
    if not verify_path_exists(file_path):
        return f"Error: file does not exist: {file_path}"
    with open(file_path, "r") as f:
        contents = f.read()
    return contents if contents else "File is empty"


def write_file_tool(file_path: str):
    pass


def bash_too():
    pass


__all__ = [
    "ls_tool",
    "ls_tool_schema",
    "read_tool",
    "read_tool_schema",
]
