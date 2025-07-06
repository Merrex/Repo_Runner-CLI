"""
Application runner functionality.
"""

import subprocess
import json
import os
import time
import signal
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from .logger import get_logger


class ApplicationRunner:
    """Handles running applications based on detected structure."""
    
    def __init__(self, path: Path, config: Dict = None, dry_run: bool = False):
        self.path = path
        self.config = config or {}
        self.dry_run = dry_run
        self.logger = get_logger()
        self.processes = []
    
    def run(self, structure: Dict[str, Any], port: Optional[int] = None, 
            host: str = 'localhost', use_docker: bool = False) -> Dict[str, Any]:
        """Run the application based on detected structure."""
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        services = {}
        
        # Decide whether to use Docker
        if use_docker or (structure.get('docker') and not self._has_direct_run_method(structure)):
            services = self._run_with_docker(structure, port, host)
        else:
            services = self._run_directly(structure, port, host)
        
        return services
    
    def _run_with_docker(self, structure: Dict[str, Any], port: Optional[int], host: str) -> Dict[str, Any]:
        """Run application using Docker."""
        self.logger.info("Running application with Docker")
        
        services = {}
        
        # Check for docker-compose
        if (self.path / 'docker-compose.yml').exists() or (self.path / 'docker-compose.yaml').exists():
            services = self._run_docker_compose(port, host)
        elif (self.path / 'Dockerfile').exists():
            services = self._run_dockerfile(port, host)
        else:
            self.logger.error("Docker requested but no Docker configuration found")
            raise Exception("No Docker configuration found")
        
        return services
    
    def _run_directly(self, structure: Dict[str, Any], port: Optional[int], host: str) -> Dict[str, Any]:
        """Run application directly without Docker."""
        self.logger.info("Running application directly")
        
        project_type = structure.get('type', 'unknown')
        services = {}
        
        if project_type == 'django':
            services = self._run_django(port, host)
        elif project_type == 'python-web':
            services = self._run_python_web(structure, port, host)
        elif project_type == 'nodejs':
            services = self._run_nodejs(port, host)
        elif project_type in ['react', 'vue', 'angular', 'vite-react']:
            services = self._run_frontend(structure, port, host)
        elif project_type == 'nextjs':
            services = self._run_nextjs(port, host)
        elif project_type == 'nuxtjs':
            services = self._run_nuxtjs(port, host)
        else:
            self.logger.warning(f"Unknown project type: {project_type}")
            services = self._run_fallback(structure, port, host)
        
        return services
    
    def _run_django(self, port: Optional[int], host: str) -> Dict[str, Any]:
        """Run Django application."""
        port = port or 8000
        cmd = ['python', 'manage.py', 'runserver', f'{host}:{port}']
        
        process = self._start_process(cmd, "Django server")
        
        return {
            'django': {
                'process': process,
                'url': f'http://{host}:{port}',
                'type': 'web',
                'port': port
            }
        }
    
    def _run_python_web(self, structure: Dict[str, Any], port: Optional[int], host: str) -> Dict[str, Any]:
        """Run Python web application (Flask/FastAPI)."""
        port = port or 5000
        
        # Try to detect the main file
        main_files = ['main.py', 'app.py', 'run.py', 'server.py']
        entry_point = None
        
        for file in main_files:
            if (self.path / file).exists():
                entry_point = file
                break
        
        if not entry_point:
            self.logger.error("No Python entry point found")
            raise Exception("No Python entry point found")
        
        # Set environment variables
        os.environ['HOST'] = host
        os.environ['PORT'] = str(port)
        
        cmd = ['python', entry_point]
        process = self._start_process(cmd, "Python web server")
        
        return {
            'python-web': {
                'process': process,
                'url': f'http://{host}:{port}',
                'type': 'web',
                'port': port
            }
        }
    
    def _run_nodejs(self, port: Optional[int], host: str) -> Dict[str, Any]:
        """Run Node.js application."""
        port = port or 3000
        
        # Check package.json for start script
        package_json = self.path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    scripts = data.get('scripts', {})
                    
                    if 'start' in scripts:
                        cmd = ['npm', 'start']
                    elif 'dev' in scripts:
                        cmd = ['npm', 'run', 'dev']
                    else:
                        cmd = ['node', 'index.js']
            except:
                cmd = ['node', 'index.js']
        else:
            cmd = ['node', 'index.js']
        
        # Set environment variables
        os.environ['HOST'] = host
        os.environ['PORT'] = str(port)
        
        process = self._start_process(cmd, "Node.js server")
        
        return {
            'nodejs': {
                'process': process,
                'url': f'http://{host}:{port}',
                'type': 'web',
                'port': port
            }
        }
    
    def _run_frontend(self, structure: Dict[str, Any], port: Optional[int], host: str) -> Dict[str, Any]:
        """Run frontend application."""
        port = port or 3000
        
        # Check package.json for dev script
        package_json = self.path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    scripts = data.get('scripts', {})
                    
                    if 'dev' in scripts:
                        cmd = ['npm', 'run', 'dev']
                    elif 'start' in scripts:
                        cmd = ['npm', 'start']
                    elif 'serve' in scripts:
                        cmd = ['npm', 'run', 'serve']
                    else:
                        cmd = ['npm', 'run', 'dev']
            except:
                cmd = ['npm', 'run', 'dev']
        else:
            cmd = ['npm', 'run', 'dev']
        
        # Set environment variables
        os.environ['HOST'] = host
        os.environ['PORT'] = str(port)
        
        process = self._start_process(cmd, "Frontend dev server")
        
        return {
            'frontend': {
                'process': process,
                'url': f'http://{host}:{port}',
                'type': 'web',
                'port': port
            }
        }
    
    def _run_nextjs(self, port: Optional[int], host: str) -> Dict[str, Any]:
        """Run Next.js application."""
        port = port or 3000
        
        # Set environment variables
        os.environ['HOST'] = host
        os.environ['PORT'] = str(port)
        
        cmd = ['npm', 'run', 'dev']
        process = self._start_process(cmd, "Next.js server")
        
        return {
            'nextjs': {
                'process': process,
                'url': f'http://{host}:{port}',
                'type': 'web',
                'port': port
            }
        }
    
    def _run_nuxtjs(self, port: Optional[int], host: str) -> Dict[str, Any]:
        """Run Nuxt.js application."""
        port = port or 3000
        
        # Set environment variables
        os.environ['HOST'] = host
        os.environ['PORT'] = str(port)
        
        cmd = ['npm', 'run', 'dev']
        process = self._start_process(cmd, "Nuxt.js server")
        
        return {
            'nuxtjs': {
                'process': process,
                'url': f'http://{host}:{port}',
                'type': 'web',
                'port': port
            }
        }
    
    def _run_docker_compose(self, port: Optional[int], host: str) -> Dict[str, Any]:
        """Run application using docker-compose."""
        cmd = ['docker-compose', 'up', '--build']
        
        # Add detached mode for automation
        if self.config.get('detached', False):
            cmd.append('-d')
        
        process = self._start_process(cmd, "Docker Compose")
        
        # Try to detect exposed ports from docker-compose.yml
        services = self._parse_docker_compose_services()
        
        return services
    
    def _run_dockerfile(self, port: Optional[int], host: str) -> Dict[str, Any]:
        """Run application using Dockerfile."""
        port = port or 8000
        
        # Build image
        build_cmd = ['docker', 'build', '-t', 'repo-runner-app', '.']
        self._run_command(build_cmd, "Building Docker image")
        
        # Run container
        run_cmd = ['docker', 'run', '-p', f'{port}:{port}', 'repo-runner-app']
        
        if self.config.get('detached', False):
            run_cmd.insert(2, '-d')
        
        process = self._start_process(run_cmd, "Docker container")
        
        return {
            'docker': {
                'process': process,
                'url': f'http://{host}:{port}',
                'type': 'web',
                'port': port
            }
        }
    
    def _run_fallback(self, structure: Dict[str, Any], port: Optional[int], host: str) -> Dict[str, Any]:
        """Fallback run method for unknown project types."""
        self.logger.warning("Using fallback run method")
        
        # Try common start commands
        commands = [
            ['npm', 'start'],
            ['npm', 'run', 'dev'],
            ['python', 'main.py'],
            ['python', 'app.py'],
            ['node', 'index.js'],
            ['node', 'server.js']
        ]
        
        for cmd in commands:
            if self._command_exists(cmd[0]) and self._file_exists_for_command(cmd):
                process = self._start_process(cmd, "Application (fallback)")
                return {
                    'fallback': {
                        'process': process,
                        'url': f'http://{host}:{port or 3000}',
                        'type': 'web',
                        'port': port or 3000
                    }
                }
        
        raise Exception("No suitable run method found")
    
    def _start_process(self, cmd: List[str], description: str):
        """Start a process and add it to the process list."""
        self.logger.info(f"Starting {description}: {' '.join(cmd)}")
        
        if self.dry_run:
            self.logger.info("DRY RUN: Process not started")
            return None
        
        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            self.processes.append(process)
            
            # Wait a moment to check if process started successfully
            time.sleep(2)
            
            if process.poll() is not None:
                # Process has already terminated
                stdout, stderr = process.communicate()
                self.logger.error(f"Process failed to start: {stdout}")
                raise Exception(f"Process failed to start: {stdout}")
            
            self.logger.info(f"✅ {description} started successfully (PID: {process.pid})")
            return process
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start {description}: {e}")
            raise
    
    def _run_command(self, cmd: List[str], description: str) -> bool:
        """Run a command synchronously."""
        self.logger.info(f"{description}: {' '.join(cmd)}")
        
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
                self.logger.info(f"✅ {description} completed successfully")
                return True
            else:
                self.logger.error(f"❌ {description} failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ {description} failed: {e}")
            return False
    
    def _has_direct_run_method(self, structure: Dict[str, Any]) -> bool:
        """Check if we have a direct run method for this project type."""
        project_type = structure.get('type', 'unknown')
        return project_type in [
            'django', 'python-web', 'nodejs', 'react', 'vue', 
            'angular', 'nextjs', 'nuxtjs', 'vite-react'
        ]
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists."""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _file_exists_for_command(self, cmd: List[str]) -> bool:
        """Check if the required file exists for a command."""
        if len(cmd) < 2:
            return True
        
        file_arg = cmd[1]
        return (self.path / file_arg).exists()
    
    def _parse_docker_compose_services(self) -> Dict[str, Any]:
        """Parse docker-compose.yml to extract service information."""
        # This is a simplified parser - in production, you'd use a proper YAML parser
        compose_files = ['docker-compose.yml', 'docker-compose.yaml']
        
        for compose_file in compose_files:
            if (self.path / compose_file).exists():
                # For now, return a default service
                return {
                    'docker-compose': {
                        'process': None,
                        'url': 'http://localhost:8000',
                        'type': 'web',
                        'port': 8000
                    }
                }
        
        return {}
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop_all_processes()
        sys.exit(0)
    
    def stop_all_processes(self):
        """Stop all running processes."""
        for process in self.processes:
            if process and process.poll() is None:
                self.logger.info(f"Stopping process {process.pid}")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()