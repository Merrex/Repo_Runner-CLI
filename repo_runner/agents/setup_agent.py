import subprocess
import json
import os
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent
import subprocess
import sys
import os

class SetupAgent(BaseAgent):
    def run(self, *args, **kwargs):
        """Setup and configure project environment"""
        repo_path = kwargs.get('repo_path', '.')
        detection_result = kwargs.get('detection_result', {})
        
        try:
            # Use the existing setup logic
            setup_result = self.setup_project(repo_path)
            
            result = {
                "status": "ok",
                "agent": self.agent_name,
                "setup": setup_result,
                "repo_path": repo_path,
                "services_configured": len(detection_result.get('services', []))
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

    def _install_pip_requirements(self, req_path):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_path], capture_output=True, text=True)
            return {"returncode": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}

    def _install_conda_env(self, conda_path):
        try:
            result = subprocess.run(['conda', 'env', 'update', '-f', conda_path], capture_output=True, text=True)
            return {"returncode": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}

    def _install_npm_packages(self, dir_path):
        try:
            result = subprocess.run(['npm', 'install'], cwd=dir_path, capture_output=True, text=True)
            return {"returncode": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}

    def _install_yarn_packages(self, dir_path):
        try:
            result = subprocess.run(['yarn', 'install'], cwd=dir_path, capture_output=True, text=True)
            return {"returncode": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)} 