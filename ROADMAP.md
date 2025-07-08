# Repo_Runner-CLI Roadmap

## 🧠 Agentic Microservice Milestone (2024)

### Architecture
- Modular agent design: BaseAgent + 5 core agents (setup, env, deps, run, fix)
- OrchestratorAgent coordinates all agents, logs to run_state.json
- CLI entrypoint with all required flags
- All state and logs are file-based for traceability
- Ready for parent project and agent-to-agent calls

### Completed Steps
- [x] BaseAgent with run, retry, checkpoint, log_result, report_error
- [x] SetupAgent, EnvDetectorAgent, DependencyAgent, RunnerAgent, FixerAgent stubs
- [x] OrchestratorAgent (admin orchestrator) with stepwise agent calls and logging
- [x] orchestrator_cli.py with all required CLI flags
- [x] __init__.py exports run_orchestrator for parent/agent calls
- [x] All agent logs and run state are file-based

### Next Steps
- [ ] Implement real logic for each agent (env detection, dependency alignment, etc.)
- [ ] Add advanced LLM, RAG, and model fallback logic
- [ ] Integrate with parent project UnifiedOrchestrator
- [ ] Add API wrapper (FastAPI) for UI/dashboard
- [ ] Expand test coverage and CI

## See TRACKER.md for a step-by-step implementation log. 