from .file_agent import FileAgent
from typing import Dict, Optional
import os

class ConfigAgent(FileAgent):
    """
    Agent responsible for creating and updating configuration files (ngrok config, .env, etc.)
    
    Agentic OOP Pattern:
    - Inherits from FileAgent, gaining all generic file operations.
    - Adds config-specific logic (templating, validation, etc.).
    - Can be used by any agent (PortManagerAgent, OrchestratorAgent, etc.) for config file creation.
    - Supports agentic interoperability and dynamic invocation at any checkpoint.
    """
    def create_ngrok_config(self, authtoken: str, tunnels: Dict[str, int], config_path: Optional[str] = None) -> str:
        """
        Create an ngrok config file for multiplexing tunnels.
        Args:
            authtoken: The ngrok authentication token.
            tunnels: Dict of {name: port} for each tunnel.
            config_path: Optional path to write the config file. Defaults to ~/.config/ngrok/ngrok.yml
        Returns:
            The path to the config file.
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.config/ngrok/ngrok.yml")
        tunnels_yaml = "\n".join([f"  {name}:\n    addr: {port}\n    proto: http" for name, port in tunnels.items()])
        config_content = f"authtoken: {authtoken}\ntunnels:\n{tunnels_yaml}\n"
        return self.write_file(config_path, config_content)

    def create_env_file(self, env_vars: Dict[str, str], path: str = ".env") -> str:
        """
        Create or update a .env file with the given variables.
        Args:
            env_vars: Dict of environment variables to write.
            path: Path to the .env file (default: .env in current directory).
        Returns:
            The path to the .env file.
        """
        lines = [f"{k}={v}" for k, v in env_vars.items()]
        content = "\n".join(lines) + "\n"
        return self.write_file(path, content) 