# Project Architecture Overview

## Key Concepts

### Managers
- **Location:** `repo_runner/managers/`
- **Role:** Decision-makers. Coordinate workflow, select and invoke agents at checkpoints, and manage high-level logic.
- **Models:** Use decision-making models to determine which agent(s) to use and when.
- **Inheritance:** All managers inherit from `BaseManager` for consistency and extensibility.
- **Examples:**
  - `Orchestrator`: Coordinates the entire workflow.
  - `ModelManager`: Handles model selection and configuration.
  - `PortManagerAgent`: Manages port allocation and environment-specific access.

### Agents
- **Location:** `repo_runner/agents/`
- **Role:** Technical specialists. Perform generative or technical tasks (e.g., code generation, file management, health checks).
- **Models:** Use generative models for their specialized tasks.
- **Inheritance:** All agents inherit from `BaseAgent` for consistency and extensibility.
- **Examples:**
  - `FileAgent`, `ConfigAgent`, `DependencyAgent`, `DetectionAgent`, `FixerAgent`, `DBAgent`, `RequirementsAgent`, `HealthAgent`, `RunnerAgent`, `SetupAgent`

### Models
- **Location:** `repo_runner/agents/llm/` (utilities and configs)
- **Usage:** Used by both managers and agents. Managers use models for decision-making; agents use models for generative tasks.

## Parent-Child Relationships
- **Managers and agents can have inheritance hierarchies** to promote abstraction, reusability, and security.
- **Base classes:**
  - `BaseManager` (in `managers/base_manager.py`)
  - `BaseAgent` (in `agents/base_agent.py`)
- **Example:**
  - `ConfigAgent` inherits from both `FileAgent` and `BaseAgent`.
  - `PortManagerAgent` and `EnvironmentAwarePortManager` inherit from `BaseManager`.

## Directory Structure

```
repo_runner/
  managers/
    base_manager.py
    orchestrator.py
    model_manager.py
    port_manager.py
  agents/
    base_agent.py
    file_agent.py
    config_agent.py
    dependency_agent.py
    detection_agent.py
    fixer_agent.py
    db_agent.py
    requirements_agent.py
    health_agent.py
    runner_agent.py
    setup_agent.py
    llm/
      llm_utils.py
      ...
```

## Flow Example
- **Orchestrator** (manager) decides which agents to use at each checkpoint.
- **Agents** perform their specialized tasks and return results to the manager.
- **Managers** can invoke other managers or agents as needed, supporting parent-child and peer relationships.

## Benefits
- **Separation of concerns:** Clear distinction between decision logic (managers) and technical execution (agents).
- **Extensibility:** Easy to add new managers or agents.
- **Reusability:** Agents can be reused by multiple managers.
- **Security and abstraction:** Parent-child relationships allow for encapsulation and controlled access. 