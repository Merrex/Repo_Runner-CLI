import subprocess
import json
import os
import time
import signal
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm

class RunnerAgent:
    def start(self, structure, mode="local"):
        """Start the application using LLM for intelligent execution."""
        files = structure.get('files', {})
        
        # Get the repository path from structure
        repo_path = structure.get('repo_path', '.')
        
        runner_results = {
            'started_services': [],
            'processes': [],
            'ports': [],
            'urls': [],
            'errors': [],
            'warnings': []
        }
        
        # Determine how to start the application
        start_method = self._determine_start_method(structure, mode)
        runner_results['start_method'] = start_method
        
        if start_method == 'docker':
            result = self._start_with_docker(structure, mode, repo_path)
        elif start_method == 'python':
            result = self._start_python_app(structure, mode, repo_path)
        elif start_method == 'node':
            result = self._start_node_app(structure, mode, repo_path)
        else:
            result = self._start_generic_app(structure, mode, repo_path)
        
        runner_results.update(result)
        
        return runner_results
    
    def _determine_start_method(self, structure, mode):
        """Determine the best way to start the application using LLM."""
        files = structure.get('files', {})
        
        # First try rule-based detection
        if 'docker-compose.yml' in files or 'Dockerfile' in files:
            return 'docker'
        elif 'package.json' in files:
            return 'node'
        elif any(f.endswith('.py') for f in files.keys()):
            return 'python'
        
        # Fallback to LLM if rule-based detection fails
        try:
            prompt = f"""
            Analyze this project and determine the best way to start it:
            
            Mode: {mode}
            Files: {list(files.keys())}
            Technologies: {structure.get('technologies', [])}
            
            Common start methods:
            - docker: If Dockerfile or docker-compose.yml exists
            - python: If main.py, app.py, or manage.py exists
            - node: If package.json with start script exists
            - generic: For other cases
            
            Consider:
            - Available files
            - Technology stack
            - Mode (local vs cloud)
            - Best practices
            
            Return only: docker, python, node, or generic
            """
            
            method = generate_code_with_llm(prompt, agent_name='setup_agent').strip().lower()
            
            # Validate the response
            valid_methods = ['docker', 'python', 'node', 'generic']
            return method if method in valid_methods else 'generic'
        except Exception as e:
            print(f"LLM detection failed: {e}, using generic method")
            return 'generic'
    
    def _start_with_docker(self, structure, mode, repo_path):
        """Start application using Docker."""
        try:
            # Rule-based Docker command selection
            docker_cmd = None
            if os.path.exists(os.path.join(repo_path, 'docker-compose.yml')):
                docker_cmd = 'docker-compose up -d' if mode == 'cloud' else 'docker-compose up'
            elif os.path.exists(os.path.join(repo_path, 'Dockerfile')):
                docker_cmd = 'docker build -t app . && docker run -p 8000:8000 app'
            else:
                docker_cmd = 'docker-compose up'
            
            print(f"🚀 Starting Docker application with: {docker_cmd}")
            
            # Execute Docker command
            process = subprocess.Popen(
                docker_cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=repo_path
            )
            
            # Wait a bit for the process to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ Docker application started successfully!")
                return {
                    'started_services': ['docker'],
                    'processes': [{'type': 'docker', 'pid': process.pid, 'command': docker_cmd}],
                    'ports': [8000],  # Default port
                    'urls': ['http://localhost:8000'],
                    'docker_command': docker_cmd,
                    'status': 'running'
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    'errors': [f"Docker start failed: {stderr}"],
                    'docker_command': docker_cmd,
                    'status': 'failed'
                }
            
        except Exception as e:
            return {'errors': [f"Docker start failed: {e}"]}
    
    def _start_python_app(self, structure, mode, repo_path):
        """Start Python application."""
        try:
            # Rule-based Python command selection
            python_cmd = None
            if os.path.exists(os.path.join(repo_path, 'main.py')):
                python_cmd = 'python main.py'
            elif os.path.exists(os.path.join(repo_path, 'app.py')):
                python_cmd = 'python app.py'
            elif os.path.exists(os.path.join(repo_path, 'manage.py')):
                python_cmd = 'python manage.py runserver'
            else:
                python_cmd = 'python -m http.server 8000'  # Fallback
            
            print(f"🚀 Starting Python application with: {python_cmd}")
            
            # Execute Python command
            process = subprocess.Popen(
                python_cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=repo_path
            )
            
            # Wait a bit for the process to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ Python application started successfully!")
                return {
                    'started_services': ['python'],
                    'processes': [{'type': 'python', 'pid': process.pid, 'command': python_cmd}],
                    'ports': [8000],  # Default port
                    'urls': ['http://localhost:8000'],
                    'python_command': python_cmd,
                    'status': 'running'
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    'errors': [f"Python start failed: {stderr}"],
                    'python_command': python_cmd,
                    'status': 'failed'
                }
            
        except Exception as e:
            return {'errors': [f"Python start failed: {e}"]}
    
    def _start_node_app(self, structure, mode, repo_path):
        """Start Node.js application."""
        try:
            # Rule-based Node.js command selection
            node_cmd = None
            package_json_path = os.path.join(repo_path, 'package.json')
            
            if os.path.exists(package_json_path):
                # Check for start script
                try:
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)
                        scripts = package_data.get('scripts', {})
                        if 'start' in scripts:
                            node_cmd = 'npm start'
                        elif 'dev' in scripts:
                            node_cmd = 'npm run dev'
                        else:
                            node_cmd = 'npm start'
                except:
                    node_cmd = 'npm start'
            else:
                # Look for common entry points
                if os.path.exists(os.path.join(repo_path, 'app.js')):
                    node_cmd = 'node app.js'
                elif os.path.exists(os.path.join(repo_path, 'server.js')):
                    node_cmd = 'node server.js'
                else:
                    node_cmd = 'npm start'
            
            print(f"🚀 Starting Node.js application with: {node_cmd}")
            
            # Execute Node.js command
            process = subprocess.Popen(
                node_cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=repo_path
            )
            
            # Wait a bit for the process to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ Node.js application started successfully!")
                return {
                    'started_services': ['node'],
                    'processes': [{'type': 'node', 'pid': process.pid, 'command': node_cmd}],
                    'ports': [3000],  # Default port
                    'urls': ['http://localhost:3000'],
                    'node_command': node_cmd,
                    'status': 'running'
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    'errors': [f"Node.js start failed: {stderr}"],
                    'node_command': node_cmd,
                    'status': 'failed'
                }
            
        except Exception as e:
            return {'errors': [f"Node.js start failed: {e}"]}
    
    def _start_generic_app(self, structure, mode, repo_path):
        """Start generic application."""
        try:
            # Rule-based generic command selection
            generic_cmd = None
            
            # Check for common patterns
            if os.path.exists(os.path.join(repo_path, 'docker-compose.yml')):
                generic_cmd = 'docker-compose up'
            elif os.path.exists(os.path.join(repo_path, 'package.json')):
                generic_cmd = 'npm start'
            elif os.path.exists(os.path.join(repo_path, 'main.py')):
                generic_cmd = 'python main.py'
            elif os.path.exists(os.path.join(repo_path, 'app.py')):
                generic_cmd = 'python app.py'
            else:
                generic_cmd = 'python -m http.server 8080'  # Fallback HTTP server
            
            print(f"🚀 Starting generic application with: {generic_cmd}")
            
            # Execute generic command
            process = subprocess.Popen(
                generic_cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=repo_path
            )
            
            # Wait a bit for the process to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ Generic application started successfully!")
                return {
                    'started_services': ['generic'],
                    'processes': [{'type': 'generic', 'pid': process.pid, 'command': generic_cmd}],
                    'ports': [8080],  # Default port
                    'urls': ['http://localhost:8080'],
                    'generic_command': generic_cmd,
                    'status': 'running'
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    'errors': [f"Generic start failed: {stderr}"],
                    'generic_command': generic_cmd,
                    'status': 'failed'
                }
            
        except Exception as e:
            return {'errors': [f"Generic start failed: {e}"]}
    
    def stop(self, processes):
        """Stop running processes."""
        stopped = []
        
        for process_info in processes:
            try:
                pid = process_info.get('pid')
                if pid:
                    os.kill(pid, signal.SIGTERM)
                    stopped.append(pid)
            except Exception as e:
                print(f"Failed to stop process {pid}: {e}")
        
        return {'stopped_processes': stopped} 