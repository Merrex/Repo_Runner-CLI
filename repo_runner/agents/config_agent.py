import os
from typing import Dict, Optional

class ConfigAgent:
    """
    Agent responsible for creating and updating configuration files (ngrok config, .env, etc.)
    for use by other agents in the system. Designed for agentic interoperability.
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
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        tunnels_yaml = "\n".join([f"  {name}:\n    addr: {port}\n    proto: http" for name, port in tunnels.items()])
        config_content = f"authtoken: {authtoken}\ntunnels:\n{tunnels_yaml}\n"
        with open(config_path, "w") as f:
            f.write(config_content)
        return config_path

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
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        return path 