import os
from typing import Optional

class FileAgent:
    """
    Base agent for all file operations (create, read, update, delete).
    Designed for agentic OOP inheritance and interoperability.
    """
    def write_file(self, path: str, content: str) -> str:
        """Write content to a file (overwrites if exists). Returns the file path."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path

    def read_file(self, path: str) -> str:
        """Read and return the content of a file."""
        with open(path, "r") as f:
            return f.read()

    def append_file(self, path: str, content: str) -> str:
        """Append content to a file. Returns the file path."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            f.write(content)
        return path

    def delete_file(self, path: str) -> bool:
        """Delete a file. Returns True if deleted, False if not found."""
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False

    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        return os.path.isfile(path) 