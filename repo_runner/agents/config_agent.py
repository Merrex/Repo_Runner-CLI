from .base_agent import BaseAgent
from .file_agent import FileAgent
from typing import Dict, Optional
import os

class ConfigAgent(BaseAgent):
    """
    Agent responsible for creating and updating configuration files (ngrok config, .env, etc.)
    
    Agentic OOP Pattern:
    - Inherits from FileAgent, gaining all generic file operations.
    - Adds config-specific logic (templating, validation, etc.).
    - Can be used by any agent (PortManagerAgent, OrchestratorAgent, etc.) for config file creation.
    - Supports agentic interoperability and dynamic invocation at any checkpoint.
    """
    def run(self, *args, **kwargs):
        """Process and manage configuration files"""
        repo_path = kwargs.get('repo_path', '.')
        
        try:
            # Process configuration files
            config_files = self._find_config_files(repo_path)
            env_vars = self._extract_env_vars(repo_path)
            
            result = {
                "status": "ok",
                "agent": self.agent_name,
                "config": {
                    "config_files": config_files,
                    "env_vars": env_vars,
                    "config_count": len(config_files)
                }
            }
            
            # Save checkpoint
            self.checkpoint(result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e)
            }
            self.report_error(e)
            return error_result

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

    def checkpoint(self, state: dict, checkpoint_file: str = "config_agent_state.json"):
        """
        Save the ConfigAgent's state to a checkpoint file (default: config_agent_state.json).
        Logs the checkpoint event.
        """
        import json
        self.log(f"Checkpointing ConfigAgent state to {checkpoint_file}", "info")
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log(f"Checkpoint saved to {checkpoint_file}", "info")
        except Exception as e:
            self.log(f"Failed to save checkpoint: {e}", "error")

    def report_error(self, error, context=None, error_file="config_agent_errors.json"):
        """
        Log the error and optionally save it to a file for traceability.
        """
        import json
        self.log(f"Error reported: {error} | Context: {context}", "error")
        try:
            error_record = {"error": str(error), "context": context}
            if not os.path.exists(error_file):
                with open(error_file, "w") as f:
                    json.dump([error_record], f, indent=2)
            else:
                with open(error_file, "r+") as f:
                    errors = json.load(f)
                    errors.append(error_record)
                    f.seek(0)
                    json.dump(errors, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save error report: {e}", "error") 