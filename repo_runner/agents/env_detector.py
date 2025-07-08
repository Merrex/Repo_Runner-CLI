from .base_agent import BaseAgent

class EnvDetectorAgent(BaseAgent):
    def run(self, *args, **kwargs):
        self.log_result("[EnvDetectorAgent] Detecting environment (stub)")
        return {"status": "ok", "agent": self.agent_name} 