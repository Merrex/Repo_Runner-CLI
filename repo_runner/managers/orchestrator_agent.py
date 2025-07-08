import json
import datetime
from repo_runner.agents.setup_agent import SetupAgent
from repo_runner.agents.env_detector import EnvDetectorAgent
from repo_runner.agents.dependency_agent import DependencyAgent
from repo_runner.agents.runner_agent import RunnerAgent
from repo_runner.agents.fixer_agent import FixerAgent

class OrchestratorAgent:
    def __init__(self, repo_path, env="detect", config=None):
        self.repo_path = repo_path
        self.env = env
        self.config = config or {}
        self.run_state_file = "run_state.json"
        self.state = {"steps": []}

    def run(self):
        agents = [
            ("env_detect", EnvDetectorAgent()),
            ("setup", SetupAgent()),
            ("dependency", DependencyAgent()),
            ("runner", RunnerAgent()),
            ("fixer", FixerAgent()),
        ]
        for name, agent in agents:
            ts = datetime.datetime.now().isoformat()
            try:
                result = agent.run(repo_path=self.repo_path, env=self.env, config=self.config)
                step = {"agent": name, "timestamp": ts, "result": result}
            except Exception as e:
                step = {"agent": name, "timestamp": ts, "error": str(e)}
            self.state["steps"].append(step)
            self._save_state()
        return self.state

    def _save_state(self):
        with open(self.run_state_file, "w") as f:
            json.dump(self.state, f, indent=2) 