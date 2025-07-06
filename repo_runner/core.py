"""
Core functionality for repo_runner.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from .detectors import ProjectDetector
from .installers import DependencyInstaller
from .environment import EnvironmentManager
from .database import DatabaseManager
from .runner import ApplicationRunner
from .health import HealthChecker
from .documentation import DocumentationUpdater
from .hooks import HookManager
from .logger import get_logger


class RepoRunner:
    """Main class for repository detection and execution."""
    
    def __init__(self, path: str = '.', config=None, dry_run: bool = False):
        self.path = Path(path).resolve()
        self.config = config or {}
        self.dry_run = dry_run
        self.logger = get_logger()
        
        # Initialize managers
        self.detector = ProjectDetector(self.path)
        self.installer = DependencyInstaller(self.path, config, dry_run)
        self.env_manager = EnvironmentManager(self.path, config, dry_run)
        self.db_manager = DatabaseManager(self.path, config, dry_run)
        self.app_runner = ApplicationRunner(self.path, config, dry_run)
        self.health_checker = HealthChecker(self.path, config)
        self.doc_updater = DocumentationUpdater(self.path, config, dry_run)
        self.hook_manager = HookManager(self.path, config)
        
        self.structure = None
        self.services = {}
    
    def detect_structure(self) -> Dict[str, Any]:
        """Detect project structure and technologies."""
        self.logger.info(f"Detecting project structure in {self.path}")
        
        # Run pre-detection hooks
        self.hook_manager.run_hooks('pre_detect')
        
        self.structure = self.detector.detect()
        
        # Run post-detection hooks
        self.hook_manager.run_hooks('post_detect', structure=self.structure)
        
        return self.structure
    
    def install_dependencies(self):
        """Install project dependencies."""
        if not self.structure:
            self.detect_structure()
        
        self.logger.info("Installing dependencies")
        
        # Run pre-install hooks
        self.hook_manager.run_hooks('pre_install', structure=self.structure)
        
        self.installer.install_all(self.structure)
        
        # Run post-install hooks
        self.hook_manager.run_hooks('post_install', structure=self.structure)
    
    def setup_environment(self):
        """Setup environment variables and configuration."""
        if not self.structure:
            self.detect_structure()
        
        self.logger.info("Setting up environment")
        
        # Run pre-env hooks
        self.hook_manager.run_hooks('pre_env', structure=self.structure)
        
        self.env_manager.setup(self.structure)
        
        # Run post-env hooks
        self.hook_manager.run_hooks('post_env', structure=self.structure)
    
    def setup_database(self):
        """Setup and bootstrap database."""
        if not self.structure:
            self.detect_structure()
        
        self.logger.info("Setting up database")
        
        # Run pre-db hooks
        self.hook_manager.run_hooks('pre_db', structure=self.structure)
        
        self.db_manager.setup(self.structure)
        
        # Run post-db hooks
        self.hook_manager.run_hooks('post_db', structure=self.structure)
    
    def run_application(self, port: Optional[int] = None, host: str = 'localhost', 
                       use_docker: bool = False):
        """Run the detected application."""
        if not self.structure:
            self.detect_structure()
        
        self.logger.info("Starting application")
        
        # Run pre-run hooks
        self.hook_manager.run_hooks('pre_run', structure=self.structure)
        
        self.services = self.app_runner.run(
            self.structure, port=port, host=host, use_docker=use_docker
        )
        
        # Run post-run hooks
        self.hook_manager.run_hooks('post_run', structure=self.structure, services=self.services)
        
        return self.services
    
    def perform_health_check(self) -> bool:
        """Perform health check on running services."""
        if not self.services:
            self.logger.warning("No services to check")
            return False
        
        self.logger.info("Performing health check")
        
        # Run pre-health hooks
        self.hook_manager.run_hooks('pre_health', services=self.services)
        
        result = self.health_checker.check_all(self.services)
        
        # Run post-health hooks
        self.hook_manager.run_hooks('post_health', services=self.services, result=result)
        
        return result
    
    def show_service_urls(self):
        """Display service URLs."""
        if not self.services:
            self.logger.warning("No services running")
            return
        
        print("\n🌐 Service URLs:")
        print("=" * 50)
        
        for service_name, service_info in self.services.items():
            if 'url' in service_info:
                status = "✅" if service_info.get('healthy', False) else "❌"
                print(f"{status} {service_name}: {service_info['url']}")
        
        print("=" * 50)
    
    def update_documentation(self):
        """Update project documentation."""
        if not self.structure:
            self.detect_structure()
        
        self.logger.info("Updating documentation")
        
        # Run pre-docs hooks
        self.hook_manager.run_hooks('pre_docs', structure=self.structure)
        
        self.doc_updater.update(self.structure, self.services)
        
        # Run post-docs hooks
        self.hook_manager.run_hooks('post_docs', structure=self.structure)
    
    def print_detection_summary(self, structure: Dict[str, Any]):
        """Print a formatted summary of detected structure."""
        print("\n🔍 Project Detection Summary:")
        print("=" * 50)
        
        # Project type
        project_type = structure.get('type', 'unknown')
        print(f"Project Type: {project_type}")
        
        # Technologies
        technologies = structure.get('technologies', [])
        if technologies:
            print(f"Technologies: {', '.join(technologies)}")
        
        # Components
        components = structure.get('components', {})
        if components:
            print("\nComponents:")
            for component, info in components.items():
                print(f"  • {component}: {info.get('type', 'detected')}")
        
        # Database
        database = structure.get('database')
        if database:
            print(f"\nDatabase: {database.get('type', 'unknown')}")
        
        # Docker
        if structure.get('docker'):
            print("Docker: Available")
        
        # CI/CD
        ci_cd = structure.get('ci_cd', [])
        if ci_cd:
            print(f"CI/CD: {', '.join(ci_cd)}")
        
        print("=" * 50)