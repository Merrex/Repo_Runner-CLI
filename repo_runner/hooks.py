"""
Hook system for extensibility.
"""

import importlib.util
import os
from pathlib import Path
from typing import Dict, Any, Callable, List
from .logger import get_logger


class HookManager:
    """Manages hooks for extensibility."""
    
    def __init__(self, path: Path, config: Dict = None):
        self.path = path
        self.config = config or {}
        self.logger = get_logger()
        self.hooks: Dict[str, List[Callable]] = {}
        self._load_hooks()
    
    def _load_hooks(self):
        """Load hooks from configuration and hook files."""
        # Load hooks from config
        config_hooks = self.config.get('hooks', {})
        for hook_name, hook_functions in config_hooks.items():
            if isinstance(hook_functions, list):
                self.hooks[hook_name] = hook_functions
            else:
                self.hooks[hook_name] = [hook_functions]
        
        # Load hooks from hooks.py file
        hooks_file = self.path / 'hooks.py'
        if hooks_file.exists():
            self._load_hooks_from_file(hooks_file)
        
        # Load hooks from .repo_runner directory
        hooks_dir = self.path / '.repo_runner' / 'hooks'
        if hooks_dir.exists():
            self._load_hooks_from_directory(hooks_dir)
    
    def _load_hooks_from_file(self, hooks_file: Path):
        """Load hooks from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location("hooks", hooks_file)
            hooks_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hooks_module)
            
            # Look for hook functions
            for attr_name in dir(hooks_module):
                if attr_name.startswith('pre_') or attr_name.startswith('post_'):
                    hook_func = getattr(hooks_module, attr_name)
                    if callable(hook_func):
                        self.register_hook(attr_name, hook_func)
                        self.logger.info(f"Loaded hook: {attr_name}")
        
        except Exception as e:
            self.logger.error(f"Failed to load hooks from {hooks_file}: {e}")
    
    def _load_hooks_from_directory(self, hooks_dir: Path):
        """Load hooks from a directory of Python files."""
        for hook_file in hooks_dir.glob('*.py'):
            if hook_file.name.startswith('_'):
                continue  # Skip private files
            
            try:
                spec = importlib.util.spec_from_file_location(
                    f"hooks.{hook_file.stem}", hook_file
                )
                hook_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(hook_module)
                
                # Look for hook functions
                for attr_name in dir(hook_module):
                    if attr_name.startswith('pre_') or attr_name.startswith('post_'):
                        hook_func = getattr(hook_module, attr_name)
                        if callable(hook_func):
                            self.register_hook(attr_name, hook_func)
                            self.logger.info(f"Loaded hook: {attr_name} from {hook_file.name}")
            
            except Exception as e:
                self.logger.error(f"Failed to load hooks from {hook_file}: {e}")
    
    def register_hook(self, hook_name: str, hook_function: Callable):
        """Register a hook function."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(hook_function)
    
    def run_hooks(self, hook_name: str, **kwargs):
        """Run all hooks for a given hook name."""
        if hook_name not in self.hooks:
            return
        
        self.logger.debug(f"Running hooks for: {hook_name}")
        
        for hook_func in self.hooks[hook_name]:
            try:
                hook_func(**kwargs)
                self.logger.debug(f"Hook executed successfully: {hook_func.__name__}")
            except Exception as e:
                self.logger.error(f"Hook {hook_func.__name__} failed: {e}")
    
    def list_hooks(self) -> Dict[str, List[str]]:
        """List all registered hooks."""
        return {
            hook_name: [func.__name__ for func in funcs]
            for hook_name, funcs in self.hooks.items()
        }
    
    def create_hook_template(self):
        """Create a template hooks.py file."""
        hooks_template = '''"""
Custom hooks for repo_runner.

Available hook points:
- pre_detect: Called before project detection
- post_detect: Called after project detection
- pre_install: Called before dependency installation
- post_install: Called after dependency installation
- pre_env: Called before environment setup
- post_env: Called after environment setup
- pre_db: Called before database setup
- post_db: Called after database setup
- pre_run: Called before application run
- post_run: Called after application run
- pre_health: Called before health check
- post_health: Called after health check
- pre_docs: Called before documentation update
- post_docs: Called after documentation update
"""

def pre_install(structure=None, **kwargs):
    """Called before dependency installation."""
    print("🔧 Pre-install hook: Preparing for dependency installation")
    # Add your custom logic here


def post_install(structure=None, **kwargs):
    """Called after dependency installation."""
    print("✅ Post-install hook: Dependencies installed successfully")
    # Add your custom logic here


def pre_run(structure=None, **kwargs):
    """Called before application run."""
    print("🚀 Pre-run hook: Preparing to start application")
    # Add your custom logic here


def post_run(structure=None, services=None, **kwargs):
    """Called after application run."""
    print("🎉 Post-run hook: Application started successfully")
    # Add your custom logic here


def pre_health(services=None, **kwargs):
    """Called before health check."""
    print("🏥 Pre-health hook: Preparing health check")
    # Add your custom logic here


def post_health(services=None, result=None, **kwargs):
    """Called after health check."""
    if result:
        print("✅ Post-health hook: All services healthy")
    else:
        print("❌ Post-health hook: Some services unhealthy")
    # Add your custom logic here
'''
        
        hooks_file = self.path / 'hooks.py'
        if not hooks_file.exists():
            hooks_file.write_text(hooks_template)
            self.logger.info("✅ Created hooks.py template")
        else:
            self.logger.info("hooks.py already exists")