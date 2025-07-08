from repo_runner.managers.orchestrator import AutonomousServiceOrchestrator

class AdminAgent:
    """
    Admin agent to monitor orchestrators and spawn user/session-specific orchestrator agents.
    - Can list, monitor, and manage orchestrators.
    - Extensible for future admin features (e.g., audit, policy enforcement).
    """
    def __init__(self):
        self.orchestrators = {}

    def spawn_orchestrator(self, user_id: str = None, session_id: str = None) -> AutonomousServiceOrchestrator:
        orchestrator = AutonomousServiceOrchestrator()
        key = user_id or session_id or f"orch_{len(self.orchestrators)+1}"
        self.orchestrators[key] = orchestrator
        return orchestrator

    def list_orchestrators(self):
        return list(self.orchestrators.keys())

    def get_orchestrator(self, key: str):
        return self.orchestrators.get(key)

    def monitor_orchestrators(self):
        # Placeholder for monitoring logic (health, status, etc.)
        return {k: "active" for k in self.orchestrators}

# Usage:
# admin = AdminAgent()
# orch = admin.spawn_orchestrator(user_id="user123")
# print(admin.list_orchestrators()) 