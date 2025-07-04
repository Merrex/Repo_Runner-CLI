"""
Dependency installation functionality.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List
from .logger import get_logger


class DependencyInstaller:
    """Handles dependency installation for various package managers."""
    
    def __init__(self, path: Path, config: Dict = None, dry_run: bool = False):
        self.path = path
        self.config = config or {}
        self.dry_run = dry_run
        self.logger = get_logger()
    
    def install_all(self, structure: Dict[str, Any]):
        """Install all dependencies based on detected structure."""
        package_managers = structure.get('package_managers', [])
        
        for pm in package_managers:
            if pm == 'pip':
                self._install_pip()
            elif pm == 'poetry':
                self._install_poetry()
            elif pm == 'pipenv':
                self._install_pipenv()
            elif pm == 'npm':
                self._install_npm()
            elif pm == 'yarn':
                self._install_yarn()
            elif pm == 'pnpm':
                self._install_pnpm()
    
    def _run_command(self, cmd: List[str], description: str = None) -> bool:
        """Run a command with proper error handling."""
        if description:
            self.logger.info(f"{description}: {' '.join(cmd)}")
        else:
            self.logger.info(f"Running: {' '.join(cmd)}")
        
        if self.dry_run:
            self.logger.info("DRY RUN: Command not executed")
            return True
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.path, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ {description or 'Command'} completed successfully")
                return True
            else:
                self.logger.error(f"❌ {description or 'Command'} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ {description or 'Command'} timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ {description or 'Command'} failed: {e}")
            return False
    
    def _install_pip(self):
        """Install Python dependencies using pip."""
        requirements_files = ['requirements.txt', 'requirements-dev.txt', 'dev-requirements.txt']
        
        for req_file in requirements_files:
            req_path = self.path / req_file
            if req_path.exists():
                self._run_command(
                    ['pip', 'install', '-r', str(req_path)],
                    f"Installing Python dependencies from {req_file}"
                )
    
    def _install_poetry(self):
        """Install Python dependencies using Poetry."""
        if (self.path / 'pyproject.toml').exists():
            # Check if poetry is available
            if not self._check_command_available('poetry'):
                self.logger.warning("Poetry not found. Installing...")
                self._run_command(
                    ['pip', 'install', 'poetry'],
                    "Installing Poetry"
                )
            
            self._run_command(
                ['poetry', 'install'],
                "Installing Python dependencies with Poetry"
            )
    
    def _install_pipenv(self):
        """Install Python dependencies using Pipenv."""
        if (self.path / 'Pipfile').exists():
            if not self._check_command_available('pipenv'):
                self.logger.warning("Pipenv not found. Installing...")
                self._run_command(
                    ['pip', 'install', 'pipenv'],
                    "Installing Pipenv"
                )
            
            self._run_command(
                ['pipenv', 'install'],
                "Installing Python dependencies with Pipenv"
            )
    
    def _install_npm(self):
        """Install Node.js dependencies using npm."""
        if (self.path / 'package.json').exists():
            self._run_command(
                ['npm', 'install'],
                "Installing Node.js dependencies with npm"
            )
    
    def _install_yarn(self):
        """Install Node.js dependencies using Yarn."""
        if (self.path / 'package.json').exists():
            if not self._check_command_available('yarn'):
                self.logger.warning("Yarn not found. Installing...")
                self._run_command(
                    ['npm', 'install', '-g', 'yarn'],
                    "Installing Yarn"
                )
            
            self._run_command(
                ['yarn', 'install'],
                "Installing Node.js dependencies with Yarn"
            )
    
    def _install_pnpm(self):
        """Install Node.js dependencies using pnpm."""
        if (self.path / 'package.json').exists():
            if not self._check_command_available('pnpm'):
                self.logger.warning("pnpm not found. Installing...")
                self._run_command(
                    ['npm', 'install', '-g', 'pnpm'],
                    "Installing pnpm"
                )
            
            self._run_command(
                ['pnpm', 'install'],
                "Installing Node.js dependencies with pnpm"
            )
    
    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system."""
        try:
            result = subprocess.run(
                ['which', command] if os.name != 'nt' else ['where', command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False