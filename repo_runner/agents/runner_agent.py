import subprocess
import json
import os
import time
import signal
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .dependency_agent import DependencyAgent
from .base_agent import BaseAgent

class RunnerAgent(BaseAgent):
    """
    Agent responsible for running and managing the main application workflow.
    Uses DependencyAgent for all dependency management (agentic OOP pattern).
    """
    def __init__(self, config=None):
        super().__init__(config=config)
        self.dependency_agent = DependencyAgent(config=config)
        self.dependency_agent.ensure_packages(['requests'], upgrade=False)

    def run(self, *args, **kwargs):
        """Execute and run the target application"""
        repo_path = kwargs.get('repo_path', '.')
        detection_result = kwargs.get('detection_result', {})
        
        try:
            # Use the existing runner logic
            summary = {}
            
            # Python backend
            backend_entry = self._find_python_entry(repo_path)
            if backend_entry:
                summary['python'] = self._run_python_app(backend_entry, repo_path)
            
            # Node.js backend
            node_entry = self._find_node_entry(repo_path)
            if node_entry:
                summary['node'] = self._run_node_app(node_entry, repo_path)
            
            # Frontend (React/Vue/Next.js)
            frontend_entry = self._find_frontend_entry(repo_path)
            if frontend_entry:
                summary['frontend'] = self._run_frontend_app(frontend_entry, repo_path)
            
            result = {
                "status": "ok",
                "agent": self.agent_name,
                "summary": summary,
                "services_started": len(summary)
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

    def _find_python_entry(self, repo_path):
        # Look for main.py, app.py, manage.py (Django)
        for fname in ['main.py', 'app.py', 'manage.py']:
            fpath = os.path.join(repo_path or '.', fname)
            if os.path.exists(fpath):
                return fpath
        return None

    def _run_python_app(self, entry, repo_path):
        try:
            if entry.endswith('manage.py'):
                cmd = ['python', 'manage.py', 'runserver', '0.0.0.0:8000']
                url = 'http://localhost:8000'
            else:
                cmd = ['python', os.path.basename(entry)]
                url = 'http://localhost:5000'
            proc = subprocess.Popen(cmd, cwd=repo_path or '.', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {"cmd": cmd, "pid": proc.pid, "url": url}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}

    def _find_node_entry(self, repo_path):
        # Look for index.js, server.js
        for fname in ['index.js', 'server.js']:
            fpath = os.path.join(repo_path or '.', fname)
            if os.path.exists(fpath):
                return fpath
        return None

    def _run_node_app(self, entry, repo_path):
        try:
            cmd = ['node', os.path.basename(entry)]
            url = 'http://localhost:3000'
            proc = subprocess.Popen(cmd, cwd=repo_path or '.', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {"cmd": cmd, "pid": proc.pid, "url": url}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}

    def _find_frontend_entry(self, repo_path):
        # Look for package.json with react, vue, next, etc.
        pkg_path = os.path.join(repo_path or '.', 'package.json')
        if os.path.exists(pkg_path):
            try:
                import json
                with open(pkg_path) as f:
                    pkg = json.load(f)
                deps = pkg.get('dependencies', {})
                if any(fr in deps for fr in ['react', 'vue', 'next']):
                    return pkg_path
            except Exception:
                pass
        return None

    def _run_frontend_app(self, pkg_path, repo_path):
        try:
            # Try npm start or npm run dev
            for cmd in [['npm', 'start'], ['npm', 'run', 'dev']]:
                try:
                    proc = subprocess.Popen(cmd, cwd=repo_path or '.', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    url = 'http://localhost:3000'
                    return {"cmd": cmd, "pid": proc.pid, "url": url}
                except Exception:
                    continue
            return {"error": "Could not start frontend app"}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}
    
    def start(self, structure, mode="local", allocated_ports=None):
        """Start all detected services using LLM for intelligent execution."""
        services = structure.get('services', [])
        runner_results = {
            'started_services': [],
            'processes': [],
            'ports': [],
            'urls': [],
            'errors': [],
            'warnings': []
        }
        
        # Update structure with allocated ports if provided
        if allocated_ports:
            if 'port_config' not in structure:
                structure['port_config'] = {}
            structure['port_config']['allocated_ports'] = allocated_ports
        
        # If docker-compose is present and valid, try it first
        docker_service = next((s for s in services if s['type'] == 'docker'), None)
        if docker_service and os.path.exists(os.path.join(docker_service['path'], 'docker-compose.yml')):
            result = self._start_with_docker(structure, mode, docker_service['path'])
            runner_results.update(result)
            if result.get('status') == 'running':
                return runner_results
        # Otherwise, start each service individually
        for svc in services:
            if svc['type'] == 'python':
                result = self._start_python_app(structure, mode, svc['path'])
                runner_results['started_services'].append('python')
                runner_results['processes'].append(result.get('processes', [{}])[0])
                runner_results['ports'].extend(result.get('ports', []))
                runner_results['urls'].extend(result.get('urls', []))
                runner_results['errors'].extend(result.get('errors', []))
            elif svc['type'] == 'node':
                result = self._start_node_app(structure, mode, svc['path'])
                runner_results['started_services'].append('node')
                runner_results['processes'].append(result.get('processes', [{}])[0])
                runner_results['ports'].extend(result.get('ports', []))
                runner_results['urls'].extend(result.get('urls', []))
                runner_results['errors'].extend(result.get('errors', []))
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
            # Get port configuration
            port_config = structure.get('port_config', {})
            allocated_ports = port_config.get('allocated_ports', {})
            backend_port = allocated_ports.get('backend', 8000)
            
            # Rule-based Python command selection
            python_cmd = None
            if os.path.exists(os.path.join(repo_path, 'main.py')):
                python_cmd = f'python3 main.py --port {backend_port}'
            elif os.path.exists(os.path.join(repo_path, 'app.py')):
                python_cmd = f'python3 app.py --port {backend_port}'
            elif os.path.exists(os.path.join(repo_path, 'manage.py')):
                python_cmd = f'python3 manage.py runserver 0.0.0.0:{backend_port}'
            else:
                python_cmd = f'python3 -m http.server {backend_port}'  # Fallback
            
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
                    'ports': [backend_port],
                    'urls': [f'http://localhost:{backend_port}'],
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
            # Get port configuration
            port_config = structure.get('port_config', {})
            allocated_ports = port_config.get('allocated_ports', {})
            frontend_port = allocated_ports.get('frontend', 3000)
            
            # Rule-based Node.js command selection
            node_cmd = None
            if os.path.exists(os.path.join(repo_path, 'package.json')):
                # Check package.json for start script
                with open(os.path.join(repo_path, 'package.json'), 'r') as f:
                    package_data = json.load(f)
                
                scripts = package_data.get('scripts', {})
                if 'start' in scripts:
                    node_cmd = f'npm start -- --port {frontend_port}'
                elif 'dev' in scripts:
                    node_cmd = f'npm run dev -- --port {frontend_port}'
                else:
                    node_cmd = f'npm start -- --port {frontend_port}'
            else:
                node_cmd = f'npm start -- --port {frontend_port}'
            
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
            time.sleep(3)  # Give Node.js more time to start
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ Node.js application started successfully!")
                
                # Generate preview URLs
                preview_urls = self._generate_preview_urls(frontend_port, repo_path)
                
                return {
                    'started_services': ['node'],
                    'processes': [{'type': 'node', 'pid': process.pid, 'command': node_cmd}],
                    'ports': [frontend_port],
                    'urls': [f'http://localhost:{frontend_port}'],
                    'preview_urls': preview_urls,
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
    
    def _generate_preview_urls(self, port, repo_path):
        """Generate preview URLs for the application."""
        preview_info = {
            'main_url': f'http://localhost:{port}',
            'alternative_urls': [],
            'api_urls': [],
            'preview_notes': []
        }
        
        # Check for common frontend frameworks and add specific URLs
        if os.path.exists(os.path.join(repo_path, 'package.json')):
            try:
                with open(os.path.join(repo_path, 'package.json'), 'r') as f:
                    package_data = json.load(f)
                
                dependencies = package_data.get('dependencies', {})
                
                # React specific URLs
                if 'react' in dependencies or 'react-scripts' in dependencies:
                    preview_info['alternative_urls'].extend([
                        f'http://localhost:{port}/',
                        f'http://localhost:{port}/app',
                        f'http://localhost:{port}/home'
                    ])
                    preview_info['preview_notes'].append('React application detected')
                
                # Vue specific URLs
                elif 'vue' in dependencies:
                    preview_info['alternative_urls'].extend([
                        f'http://localhost:{port}/',
                        f'http://localhost:{port}/#/'
                    ])
                    preview_info['preview_notes'].append('Vue application detected')
                
                # Angular specific URLs
                elif 'angular' in dependencies or '@angular' in dependencies:
                    preview_info['alternative_urls'].extend([
                        f'http://localhost:{port}/',
                        f'http://localhost:{port}/app'
                    ])
                    preview_info['preview_notes'].append('Angular application detected')
                
                # Generic frontend URLs
                else:
                    preview_info['alternative_urls'].extend([
                        f'http://localhost:{port}/',
                        f'http://localhost:{port}/index.html'
                    ])
                    preview_info['preview_notes'].append('Generic frontend application')
                    
            except Exception as e:
                preview_info['preview_notes'].append(f'Could not analyze package.json: {e}')
        
        # Check for API endpoints
        api_paths = ['/api', '/api/v1', '/api/v2', '/rest', '/graphql']
        for api_path in api_paths:
            preview_info['api_urls'].append(f'http://localhost:{port}{api_path}')
        
        return preview_info
    
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

    def report_error(self, error, context=None, error_file="runner_agent_errors.json"):
        """
        Log the error and optionally save it to a file for traceability.
        """
        import json
        self.log(f"Error reported: {error} | Context: {context}", "error")
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
            self.log(f"Failed to save error report: {e}", "error")

    def checkpoint(self, state: dict, checkpoint_file: str = "runner_agent_state.json"):
        """
        Save the runner agent's state to a checkpoint file (default: runner_agent_state.json).
        Logs the checkpoint event.
        """
        import json
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log(f"Checkpoint saved to {checkpoint_file}", "info")
        except Exception as e:
            self.log(f"Failed to save checkpoint: {e}", "error") 