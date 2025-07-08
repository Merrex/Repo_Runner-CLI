# Repo Runner: Agentic Platform

## Overview

Repo Runner is a modular, agentic platform for running, fixing, and managing code repositories in local or cloud environments. It features a robust agent-manager-orchestrator architecture, advanced LLM integration, memory/telemetry, and user-friendly reporting.

## Key Features

- **Orchestrator as Endpoint/POC**: The orchestrator agent is the main interface for the user, handling all agent/manager errors, logs, and exceptions. It only requests user input if needed, otherwise provides a final user-friendly report with all relevant links and integration info.
- **Admin Agent**: Monitors orchestrators and can spawn user/session-specific orchestrator agents for custom-tailored services or integration with other agentic systems.
- **Agent Memory & Telemetry**: Advanced memory manager logs, retrieves, and analyzes agent run/fix history, and exposes APIs for streaming logs/telemetry.
- **Streaming Logs/Telemetry**: Real-time streaming of agent events for dashboard or local web UI integration.
- **Robust Agent-Manager-Orchestrator Workflow**: Dynamic function-calling, checkpointing, retry/self-heal, and run state tracking for all agentic operations.
- **ModelRouter/ModelPolicy**: Model-agnostic, pluggable routing between Zephyr, Mistral, GPT-4, etc. based on token length, task complexity, and execution cost.

## How It Works

1. **Start the Orchestrator**: The orchestrator manages all agents and managers, acting as the single point of contact for the user.
2. **Run/Manage a Repo**: The orchestrator coordinates setup, dependency management, health checks, fixes, and service startup.
3. **Error Handling**: All errors, logs, and exceptions are handled internally by the agentic team. The orchestrator only asks the user for input if absolutely necessary.
4. **Final Report**: After all steps, the orchestrator provides a user-friendly summary with backend/frontend links, integration info, and a log of all actions/fixes.
5. **Admin/Custom Orchestrators**: The admin agent can spawn and monitor orchestrators for specific users or integrations.
6. **Model Routing**: The ModelRouter/ModelPolicy automatically selects the best LLM (Zephyr, Mistral, GPT-4, etc.) for each task based on token length, complexity, and cost.

## Usage

- Run the orchestrator CLI or API entrypoint.
- Follow prompts only if the orchestrator requests user input.
- Review the final report for links, status, and integration info.
- Use the admin agent for advanced monitoring or to spawn custom orchestrators.
- The ModelRouter/ModelPolicy is used internally for all LLM calls, ensuring optimal model selection for each task.

## Testing

- The system is ready for robust, environment-aware, agentic workflows.
- All planned enhancements and checklist items are complete.
- Proceed to testing and review as described above. 