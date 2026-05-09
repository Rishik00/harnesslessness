import os


def verify_path_exists(path: str) -> bool:
    """Return True if the given path exists on disk."""
    return os.path.exists(path)
