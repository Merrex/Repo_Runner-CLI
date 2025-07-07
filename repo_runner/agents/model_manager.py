from typing import Dict, List, Optional, Tuple

class ModelManager:
    """
    Agentic ModelManager for centralized model configuration, selection, and fallback.
    - Stores model configs for each agent and tier (free, advanced, premium).
    - Provides methods to get the best model for an agent, with fallback.
    - Allows dynamic updates and listing of available models.
    - Designed for use by all agents and orchestrator.
    """
    def __init__(self, model_configs: Optional[Dict[str, Dict[str, str]]] = None):
        # Default model configs for all agents
        self.model_configs = model_configs or {
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

    def get_model(self, agent_name: str, tier_order: Tuple[str, ...] = ('premium', 'advanced', 'free')) -> Optional[str]:
        """
        Get the best available model for an agent, trying tiers in order (default: premium, advanced, free).
        Returns model name string, or None if not found.
        """
        config = self.model_configs.get(agent_name, {})
        for tier in tier_order:
            model = config.get(tier)
            if model:
                return model
        return None

    def set_model(self, agent_name: str, tier: str, model_name: str):
        """
        Set or update the model for a given agent and tier.
        """
        if agent_name not in self.model_configs:
            self.model_configs[agent_name] = {}
        self.model_configs[agent_name][tier] = model_name

    def list_models(self, agent_name: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """
        List all models for all agents, or for a specific agent if provided.
        """
        if agent_name:
            return {agent_name: self.model_configs.get(agent_name, {})}
        return self.model_configs

    def available_tiers(self, agent_name: str) -> List[str]:
        """
        List available tiers for a given agent.
        """
        return list(self.model_configs.get(agent_name, {}).keys()) 