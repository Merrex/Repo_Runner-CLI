import os
import json
from typing import List, Dict, Any

class AgentMemoryManager:
    """
    Advanced memory and telemetry manager for agentic workflows.
    - Logs, retrieves, and analyzes agent run/fix history.
    - Exposes APIs for streaming logs/telemetry.
    - Integrates with orchestrator and agents for memory-augmented reasoning.
    """
    def __init__(self, memory_file: str = "run_state.json"):
        self.memory_file = memory_file
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump({}, f)

    def log_event(self, event: Dict[str, Any]):
        state = self._load_state()
        state.setdefault("events", []).append(event)
        self._save_state(state)

    def get_recent_fixes(self, n: int = 5) -> List[Dict[str, Any]]:
        state = self._load_state()
        return state.get("fixes", [])[-n:]

    def get_history(self) -> List[Dict[str, Any]]:
        state = self._load_state()
        return state.get("history", [])

    def stream_logs(self):
        state = self._load_state()
        for event in state.get("events", []):
            yield event

    def stream_events(self):
        """
        Simulate real-time streaming of events for dashboard/UI integration.
        Yields new events as they are logged.
        """
        import time
        last_len = 0
        while True:
            state = self._load_state()
            events = state.get("events", [])
            if len(events) > last_len:
                for event in events[last_len:]:
                    yield event
                last_len = len(events)
            time.sleep(1)  # Polling interval

    def _load_state(self) -> Dict[str, Any]:
        with open(self.memory_file, "r") as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]):
        with open(self.memory_file, "w") as f:
            json.dump(state, f, indent=2)

# Usage:
# memory_manager = AgentMemoryManager()
# memory_manager.log_event({"type": "fix", "detail": ...})
# recent_fixes = memory_manager.get_recent_fixes() 
# for event in memory_manager.stream_events():
#     print(event) 