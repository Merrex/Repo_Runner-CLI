# Repo_Runner-CLI: Agentic Microservice Backend

## Overview
This project is a production-ready, modular agentic backend microservice for automated repository setup, fixing, and execution. It exposes a high-level `OrchestratorAgent` (admin orchestrator) as the main entrypoint for CLI, API, or parent project calls.

- **Agents:** Modular, single-responsibility classes for setup, environment detection, dependency alignment, running, and fixing.
- **Orchestrator:** Coordinates all agents, logs all state, and is callable from CLI or as a Python module.
- **CLI:** `orchestrator_cli.py` provides a robust CLI interface for all workflows.
- **Logging & State:** All agent actions, errors, and results are logged to `logs/agent_logs/` and `run_state.json`.

## Key Components
- `agents/base_agent.py`: Standardized agent base class with `run`, `retry`, `checkpoint`, `log_result`, and `report_error`.
- `agents/setup_agent.py`, `env_detector.py`, `dependency_agent.py`, `runner_agent.py`, `fixer_agent.py`: Specialized agents for each workflow step.
- `managers/orchestrator_agent.py`: Main orchestrator, coordinates all agents, logs to `run_state.json`.
- `orchestrator_cli.py`: CLI entrypoint with all required flags.
- `__init__.py`: Exports `run_orchestrator` for parent project or agent-to-agent calls.

## Usage
### CLI
```bash
python -m repo_runner.orchestrator_cli --repo_path /path/to/repo --env detect --model_quality balanced --config config.yaml --dry_run
```

### As a Python Module
```python
from repo_runner import run_orchestrator
run_orchestrator(repo_path='/path/to/repo', env='detect', model_quality='balanced', config='config.yaml', dry_run=False)
```

## Logging & State
- All agent logs: `logs/agent_logs/{agent}_{date}.log`
- Orchestrator state: `run_state.json`

## Extending
- Add new agents by inheriting from `BaseAgent` and implementing `run()`.
- Enhance orchestrator logic in `orchestrator_agent.py`.

## Project Status
- Fully agentic, modular, and ready for production or integration as a backend microservice.
- See `ROADMAP.md` and `TRACKER.md` for progress and implementation history. 