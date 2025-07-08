import json
import os

class BaseManager:
    """
    Base class for all managers. Managers are decision-making entities that coordinate agents and workflow.
    Inherit from this class to ensure consistent management interface and future extensibility.
    Provides checkpointing logic for saving/loading state at each step.

    Usage:
        manager = SomeManager()
        manager.save_checkpoint(state_dict)
        state = manager.load_checkpoint()
    """
    def __init__(self):
        pass

    def save_checkpoint(self, state: dict, filename: str = "agent_state.json"):
        """
        Save the current state to a JSON file (default: agent_state.json).
        """
        with open(filename, "w") as f:
            json.dump(state, f, indent=2)

    def load_checkpoint(self, filename: str = "agent_state.json") -> dict:
        """
        Load the state from a JSON file (default: agent_state.json). Returns an empty dict if not found.
        """
        if not os.path.exists(filename):
            return {}
        with open(filename, "r") as f:
            return json.load(f) 