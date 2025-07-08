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
    def run(self, repo_path=None, env=None, config=None, *args, **kwargs):
        summary = {}
        # Python dependencies
        req_path = os.path.join(repo_path or '.', 'requirements.txt')
        if os.path.exists(req_path):
            summary['pip'] = self._install_pip_requirements(req_path)
        # Conda environment
        conda_path = os.path.join(repo_path or '.', 'environment.yml')
        if os.path.exists(conda_path):
            summary['conda'] = self._install_conda_env(conda_path)
        # Node.js dependencies
        pkg_path = os.path.join(repo_path or '.', 'package.json')
        if os.path.exists(pkg_path):
            summary['npm'] = self._install_npm_packages(os.path.dirname(pkg_path))
        # Yarn
        yarn_lock = os.path.join(repo_path or '.', 'yarn.lock')
        if os.path.exists(yarn_lock):
            summary['yarn'] = self._install_yarn_packages(os.path.dirname(yarn_lock))
        self.log_result(f"[SetupAgent] Setup summary: {summary}")
        return {"status": "ok", "agent": self.agent_name, "summary": summary}

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