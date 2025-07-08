import subprocess
import sys
import importlib
from typing import List, Optional
from .base_agent import BaseAgent
import json
import os

class DependencyAgent(BaseAgent):
    """
    Agent responsible for checking, installing, and upgrading Python packages and system binaries.
    Designed for agentic, reusable dependency management. Can be called by orchestrator or any agent.
    """
    def check_package(self, package: str, import_name: Optional[str] = None) -> bool:
        """
        Check if a Python package is installed (optionally by import name).
        Returns True if import succeeds, False otherwise.
        """
        try:
            import_name = import_name or package
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False

    def install_package(self, package: str, upgrade: bool = False) -> bool:
        """
        Install (or upgrade) a Python package using pip. Returns True if successful.
        """
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', package]
            if upgrade:
                cmd.append('--upgrade')
            subprocess.check_call(cmd)
            return True
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")
            return False

    def ensure_packages(self, packages: List[str], upgrade: bool = False) -> bool:
        """
        Ensure a list of packages are installed. Installs any that are missing.
        Returns True if all are present after this call.
        """
        all_ok = True
        for pkg in packages:
            if not self.check_package(pkg):
                print(f"⚠️ {pkg} not available - attempting to install...")
                if not self.install_package(pkg, upgrade=upgrade):
                    all_ok = False
        return all_ok

    def check_binary(self, binary: str) -> bool:
        """
        Check if a system binary is available in PATH.
        """
        from shutil import which
        return which(binary) is not None

    def install_pyngrok(self) -> bool:
        """
        Ensure pyngrok and ngrok binary are installed.
        """
        if not self.check_package('pyngrok'):
            print("⚠️ pyngrok not available - attempting to install...")
            if not self.install_package('pyngrok'):
                return False
        # pyngrok should install ngrok binary automatically
        try:
            from pyngrok import ngrok
            ngrok_version = ngrok.get_ngrok_version()
            print(f"✅ pyngrok/ngrok available: {ngrok_version}")
            return True
        except Exception as e:
            print(f"❌ pyngrok/ngrok not working: {e}")
            return False

    def checkpoint(self, state: dict = None):
        state = state or self.context
        checkpoint_file = self.state_file
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log_result(f"Checkpoint saved to {checkpoint_file}")
        except Exception as e:
            self.report_error(f"Failed to save checkpoint: {e}")

    def report_error(self, error, context=None, error_file="dependency_agent_errors.json"):
        import json
        self.log_result(f"Error reported: {error} | Context: {context}", "error")
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
            self.log_result(f"Failed to save error report: {e}", "error")

    def run(self, repo_path=None, env=None, config=None, *args, **kwargs):
        # 1. Check for requirements.txt (pip)
        req_path = os.path.join(repo_path or '.', 'requirements.txt')
        pip_result = None
        if os.path.exists(req_path):
            pip_result = self._install_pip_requirements(req_path)
        # 2. Check for environment.yml (conda)
        conda_path = os.path.join(repo_path or '.', 'environment.yml')
        conda_result = None
        if os.path.exists(conda_path):
            conda_result = self._install_conda_env(conda_path)
        # 3. Check for apt.txt (apt)
        apt_path = os.path.join(repo_path or '.', 'apt.txt')
        apt_result = None
        if os.path.exists(apt_path):
            apt_result = self._install_apt_packages(apt_path)
        summary = {
            "pip": pip_result,
            "conda": conda_result,
            "apt": apt_result
        }
        self.log_result(f"[DependencyAgent] Dependency alignment summary: {summary}")
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

    def _install_apt_packages(self, apt_path):
        try:
            with open(apt_path) as f:
                pkgs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if not pkgs:
                return {"skipped": "No apt packages listed"}
            result = subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, text=True)
            result2 = subprocess.run(['sudo', 'apt-get', 'install', '-y'] + pkgs, capture_output=True, text=True)
            return {"returncode": result2.returncode, "stdout": result2.stdout[-500:], "stderr": result2.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)} 