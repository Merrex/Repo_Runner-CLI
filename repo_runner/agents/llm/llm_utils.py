from repo_runner.agents.dependency_agent import DependencyAgent
from repo_runner.managers.model_manager import get_model_manager

# Instantiate a module-level DependencyAgent for use in all LLM/model functions
_dependency_agent = DependencyAgent()

# Example usage in a function:
def ensure_llm_dependencies():
    required = ['transformers', 'torch', 'requests']
    if not _dependency_agent.ensure_packages(required, upgrade=False):
        raise ImportError("Failed to ensure LLM dependencies: " + ', '.join(required))

# Call ensure_llm_dependencies() at the start of any function that needs these packages 

# Centralized model config for all agents
MODEL_CONFIGS = {
    'detection_agent': {
        'free': 'microsoft/DialoGPT-medium',
        'advanced': 'gpt-3.5-turbo',
        'premium': 'gpt-4',
    },
    'requirements_agent': {
        'free': 'microsoft/DialoGPT-medium',
        'advanced': 'gpt-3.5-turbo',
        'premium': 'gpt-4',
    },
    'setup_agent': {
        'free': 'microsoft/DialoGPT-medium',
        'advanced': 'gpt-3.5-turbo',
        'premium': 'gpt-4',
    },
    'fixer_agent': {
        'free': 'microsoft/DialoGPT-medium',
        'advanced': 'gpt-3.5-turbo',
        'premium': 'gpt-4',
    },
    'db_agent': {
        'free': 'microsoft/DialoGPT-medium',
        'advanced': 'gpt-3.5-turbo',
        'premium': 'gpt-4',
    },
    'health_agent': {
        'free': 'microsoft/DialoGPT-small',
        'advanced': 'gpt-3.5-turbo',
        'premium': 'gpt-4',
    },
    'runner_agent': {
        'free': 'microsoft/DialoGPT-medium',
        'advanced': 'gpt-3.5-turbo',
        'premium': 'gpt-4',
    },
}

# Example: get model for agent and tier, with fallback

def get_model_for_agent(agent_name, tier_order=('premium', 'advanced', 'free')):
    """
    Get the best available model for an agent, trying tiers in order (premium, advanced, free).
    Returns model name string, or None if not found.
    """
    config = MODEL_CONFIGS.get(agent_name, {})
    for tier in tier_order:
        model = config.get(tier)
        if model:
            return model
    return None

# Usage in an agent:
# model_name = get_model_for_agent('detection_agent', tier_order=('premium', 'free')) 

def get_agent_model(agent_name, tier_order=('premium', 'advanced', 'free')):
    """
    Get the best available model for an agent using the ModelManager singleton.
    """
    model_manager = get_model_manager()
    return model_manager.get_model(agent_name, tier_order=tier_order)

# Example fallback usage in an agent:
def agentic_model_fallback(agent_name, task_fn, *args, **kwargs):
    """
    Try to run task_fn with the best model for agent_name, falling back through tiers.
    """
    model_manager = get_model_manager()
    for tier in ('premium', 'advanced', 'free'):
        model = model_manager.get_model(agent_name, tier_order=(tier,))
        if not model:
            continue
        try:
            return task_fn(model, *args, **kwargs)
        except Exception as e:
            print(f"Model {model} failed: {e}, trying next tier...")
    print(f"❌ All model tiers failed for {agent_name}.")
    return None 