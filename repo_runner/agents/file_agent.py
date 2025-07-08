import os
from typing import Optional
from .base_agent import BaseAgent

class FileAgent(BaseAgent):
    """
    Base agent for all file operations (create, read, update, delete).
    
    Agentic OOP Pattern:
    - This class is intended to be inherited by specialized file-related agents (e.g., ConfigAgent).
    - All generic file operations are implemented here for maximum code reuse and agent interoperability.
    - Any agent in the system can instantiate or receive a FileAgent (or child) to perform file tasks.
    - Top-level agents (OrchestratorAgent, RequirementAgent) can dynamically invoke any agent, including FileAgent, at any checkpoint.
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

    def checkpoint(self, state: dict, checkpoint_file: str = "file_agent_state.json"):
        """
        Save the FileAgent's state to a checkpoint file (default: file_agent_state.json).
        Logs the checkpoint event.
        """
        import json
        self.log(f"Checkpointing FileAgent state to {checkpoint_file}", "info")
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log(f"Checkpoint saved to {checkpoint_file}", "info")
        except Exception as e:
            self.log(f"Failed to save checkpoint: {e}", "error")

    def report_error(self, error, context=None, error_file="file_agent_errors.json"):
        """
        Log the error and optionally save it to a file for traceability.
        """
        import json
        self.log(f"Error reported: {error} | Context: {context}", "error")
        try:
            error_record = {"error": str(error), "context": context}
            if not os.path.exists(error_file):
                with open(error_file, "w") as f:
                    json.dump([error_record], f, indent=2)
            else:
                with open(error_file, "r+") as f:
                    errors = json.load(f)
                    errors.append(error_record)
                    f.seek(0)
                    json.dump(errors, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save error report: {e}", "error") 