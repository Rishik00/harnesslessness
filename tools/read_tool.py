import os


def verify_path_exists(path: str) -> bool:
    """Return True if the given path exists on disk."""
    return os.path.exists(path)


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


__all__ = ["read_tool", "read_tool_schema"]
