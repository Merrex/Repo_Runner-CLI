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
    
    def _start_with_docker(self, structure, mode, repo_path):
        """Start application using Docker."""
        try:
            prompt = f"""
            Suggest Docker start command for this project:
            
            Mode: {mode}
            Project structure: {json.dumps(structure, indent=2)}
            
            Options:
            - docker-compose up (if docker-compose.yml exists)
            - docker build && docker run (if Dockerfile exists)
            - docker-compose up -d (for detached mode)
            
            Consider:
            - Available Docker files
            - Mode (local vs cloud)
            - Port mappings
            - Environment variables
            
            Return only the recommended Docker command.
            """
            
            docker_cmd = generate_code_with_llm(prompt, agent_name='setup_agent')
            
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
            prompt = f"""
            Suggest Python start command for this project:
            
            Mode: {mode}
            Project structure: {json.dumps(structure, indent=2)}
            
            Common Python start commands:
            - python main.py
            - python app.py
            - python manage.py runserver (Django)
            - uvicorn main:app --reload (FastAPI)
            - flask run (Flask)
            - gunicorn app:app (Production)
            
            Consider:
            - Available Python files
            - Framework (Django, Flask, FastAPI, etc.)
            - Mode (development vs production)
            - Port configuration
            
            Return only the recommended Python command.
            """
            
            python_cmd = generate_code_with_llm(prompt, agent_name='setup_agent')
            
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
            prompt = f"""
            Suggest Node.js start command for this project:
            
            Mode: {mode}
            Project structure: {json.dumps(structure, indent=2)}
            
            Common Node.js start commands:
            - npm start
            - yarn start
            - node app.js
            - node server.js
            - npm run dev
            - yarn dev
            
            Consider:
            - Available package.json scripts
            - Framework (Express, Next.js, etc.)
            - Mode (development vs production)
            - Port configuration
            
            Return only the recommended Node.js command.
            """
            
            node_cmd = generate_code_with_llm(prompt, agent_name='setup_agent')
            
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
            prompt = f"""
            Suggest a generic start command for this project:
            
            Mode: {mode}
            Project structure: {json.dumps(structure, indent=2)}
            
            Analyze the project and suggest:
            - The main entry point
            - Appropriate start command
            - Port configuration
            - Environment setup
            
            Return only the recommended start command.
            """
            
            generic_cmd = generate_code_with_llm(prompt, agent_name='setup_agent')
            
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