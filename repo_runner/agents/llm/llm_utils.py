from repo_runner.agents.dependency_agent import DependencyAgent

# Instantiate a module-level DependencyAgent for use in all LLM/model functions
_dependency_agent = DependencyAgent()

# Example usage in a function:
def ensure_llm_dependencies():
    required = ['transformers', 'torch', 'requests']
    if not _dependency_agent.ensure_packages(required, upgrade=False):
        raise ImportError("Failed to ensure LLM dependencies: " + ', '.join(required))

# Call ensure_llm_dependencies() at the start of any function that needs these packages 