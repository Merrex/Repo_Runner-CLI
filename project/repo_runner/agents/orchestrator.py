from .detection_agent import DetectionAgent
from .requirements_agent import RequirementsAgent
from .setup_agent import SetupAgent
from .db_agent import DBAgent
from .runner_agent import RunnerAgent
from .health_agent import HealthAgent
from .fixer_agent import FixerAgent

class Orchestrator:
    def run(self, repo_path, mode="local"):
        structure = DetectionAgent().analyze(repo_path)
        reqs = RequirementsAgent().ensure_requirements(structure)
        SetupAgent().install(reqs)
        db_status = DBAgent().setup(structure)
        run_status = RunnerAgent().start(structure, mode)
        health = HealthAgent().check(run_status)
        if not health.get("ok"):
            fix = FixerAgent().fix(health.get("errors", []), structure)
            # Optionally, retry setup/run after fix
        return health 