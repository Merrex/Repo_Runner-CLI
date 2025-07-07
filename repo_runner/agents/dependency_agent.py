import subprocess
import sys
import importlib
from typing import List, Optional

class DependencyAgent:
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