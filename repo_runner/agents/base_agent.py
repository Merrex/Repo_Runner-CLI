import time
from repo_runner.logger import get_logger
import inspect

class BaseAgent:
    """
    Base class for all agents. Agents are technical specialists (e.g., code generation, command execution).
    Inherit from this class to ensure consistent agentic interface and future extensibility.
    Provides standardized logging, retry, self-fix hooks, and a function registry for manager/orchestrator use.

    Usage:
        agent = SomeAgent()
        registry = agent.get_function_registry()
        result = registry['install_dependency'](pkg='torch')
    """
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self._function_registry = self._register_functions()

    def _register_functions(self):
        # Register all public methods (not starting with _)
        registry = {}
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('_') and name not in ('log', 'retry', 'self_fix', 'get_function_registry'):
                registry[name] = method
        return registry

    def get_function_registry(self):
        """
        Returns a dict of {function_name: function_object, ...} for all public agent methods.
        """
        return self._function_registry

    def log(self, message, level="info"):
        if level == "debug":
            self.logger.debug(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)

    def retry(self, func, max_retries=3, delay=2, *args, **kwargs):
        """
        Retry a function up to max_retries times with delay (seconds) between attempts.
        Logs each attempt and error. Returns the function result or raises last exception.
        """
        attempt = 0
        while attempt < max_retries:
            try:
                self.log(f"Attempt {attempt+1}/{max_retries} for {func.__name__}", "debug")
                return func(*args, **kwargs)
            except Exception as e:
                self.log(f"Error in {func.__name__}: {e}", "error")
                attempt += 1
                if attempt < max_retries:
                    time.sleep(delay)
        raise

    def self_fix(self, error, context=None):
        """
        Placeholder for self-fix logic. Should be overridden by agents like FixerAgent.
        Logs the error and context, and returns False by default.
        """
        self.log(f"Self-fix not implemented for error: {error} | Context: {context}", "warning")
        return False

    def checkpoint(self, state: dict, checkpoint_file: str = "agent_state.json"):
        """
        Save the agent's state to a checkpoint file (default: agent_state.json).
        Logs the checkpoint event. Can be overridden by subclasses for custom logic.
        """
        import json
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log(f"Checkpoint saved to {checkpoint_file}", "info")
        except Exception as e:
            self.log(f"Failed to save checkpoint: {e}", "error")

    def to_openai_function_schema(self):
        """
        Return a list of OpenAI function-calling schemas for all public agent methods.
        """
        import inspect
        schemas = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not name.startswith('_') and name not in ('log', 'retry', 'self_fix', 'get_function_registry', 'checkpoint', 'report_error', 'to_openai_function_schema'):
                sig = inspect.signature(method)
                params = []
                for param in sig.parameters.values():
                    if param.name == 'self':
                        continue
                    param_schema = {
                        "name": param.name,
                        "type": "string",  # For simplicity, treat all as string
                        "description": str(param.annotation) if param.annotation != inspect._empty else ""
                    }
                    params.append(param_schema)
                schemas.append({
                    "name": name,
                    "description": method.__doc__ or "",
                    "parameters": params
                })
        return schemas 