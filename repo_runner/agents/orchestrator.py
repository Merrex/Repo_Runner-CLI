from .detection_agent import DetectionAgent
from .requirements_agent import RequirementsAgent
from .setup_agent import SetupAgent
from .db_agent import DBAgent
from .runner_agent import RunnerAgent
from .health_agent import HealthAgent
from .fixer_agent import FixerAgent
from .port_manager_agent import PortManagerAgent
import time
import signal
from typing import Dict, List, Any
import os
import subprocess
import threading
from pathlib import Path
import json
import yaml

class AutonomousServiceOrchestrator:
    """Fully autonomous service orchestrator with environment awareness"""
    
    def __init__(self):
        self.running_services = {}
        self.service_processes = {}
        self.port_manager = None  # Will be set by main orchestrator
        self.environment = self.detect_environment()
        self.service_dependencies = {}
        self.startup_order = []
        
    def detect_environment(self) -> str:
        """Detect the current environment"""
        if 'COLAB_GPU' in os.environ or 'COLAB_TPU' in os.environ:
            return 'colab'
        elif 'KUBERNETES_SERVICE_HOST' in os.environ:
            return 'kubernetes'
        elif os.path.exists('/.dockerenv'):
            return 'docker'
        elif 'AWS_EXECUTION_ENV' in os.environ:
            return 'aws'
        else:
            return 'local'
    
    def orchestrate_services(self, repo_path: str, detection_results: Dict[str, Any], port_manager=None) -> Dict[str, Any]:
        """Fully autonomous service orchestration"""
        print("🚀 Starting autonomous service orchestration...")
        
        self.port_manager = port_manager
        
        try:
            # 1. Analyze service dependencies
            self.analyze_service_dependencies(detection_results)
            
            # 2. Determine startup order
            self.determine_startup_order()
            
            # 3. Setup environment-specific configurations
            self.setup_environment_configs()
            
            # 4. Start services in correct order
            startup_results = self.start_services_sequentially(repo_path)
            
            # 5. Monitor and validate services
            health_results = self.monitor_services()
            
            # 6. Generate access URLs
            access_urls = self.generate_access_urls()
            
            return {
                'status': 'success',
                'services_started': len(self.running_services),
                'startup_order': self.startup_order,
                'health_status': health_results,
                'access_urls': access_urls,
                'environment': self.environment
            }
            
        except Exception as e:
            print(f"❌ Service orchestration failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'services_started': 0
            }
    
    def analyze_service_dependencies(self, detection_results: Dict[str, Any]):
        """Analyze service dependencies to determine startup order"""
        print("🔍 Analyzing service dependencies...")
        
        services = detection_results.get('services', {})
        self.service_dependencies = {}
        
        for service_path, service_info in services.items():
            service_name = service_info.get('name', 'unknown')
            service_type = service_info.get('type', 'unknown')
            framework = service_info.get('framework', 'unknown')
            role = service_info.get('role', 'unknown')
            
            # Determine dependencies based on service type and role
            dependencies = self.determine_service_dependencies(service_info)
            
            self.service_dependencies[service_name] = {
                'path': service_path,
                'type': service_type,
                'framework': framework,
                'role': role,
                'dependencies': dependencies,
                'info': service_info
            }
        
        print(f"✅ Analyzed {len(self.service_dependencies)} services")
    
    def determine_service_dependencies(self, service_info: Dict[str, Any]) -> List[str]:
        """Determine what other services this service depends on"""
        dependencies = []
        service_type = service_info.get('type', 'unknown')
        role = service_info.get('role', 'unknown')
        
        # Database dependencies
        if role == 'backend':
            # Check if backend needs database
            if service_type == 'python':
                if 'django' in str(service_info.get('requirements', [])):
                    dependencies.append('database')
                elif 'flask' in str(service_info.get('requirements', [])):
                    dependencies.append('database')
            elif service_type == 'node':
                if 'mongoose' in str(service_info.get('dependencies', [])):
                    dependencies.append('database')
                elif 'sequelize' in str(service_info.get('dependencies', [])):
                    dependencies.append('database')
        
        # Frontend depends on backend
        if role == 'frontend':
            dependencies.append('backend')
        
        # Redis dependencies
        if 'redis' in str(service_info.get('dependencies', [])):
            dependencies.append('redis')
        
        return dependencies
    
    def determine_startup_order(self):
        """Determine the correct startup order based on dependencies"""
        print("📋 Determining service startup order...")
        
        # Create dependency graph
        dependency_graph = {}
        for service_name, service_data in self.service_dependencies.items():
            dependency_graph[service_name] = service_data['dependencies']
        
        # Topological sort to determine startup order
        self.startup_order = self.topological_sort(dependency_graph)
        
        print(f"✅ Startup order determined: {' -> '.join(self.startup_order)}")
    
    def topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort to determine startup order"""
        # Kahn's algorithm
        in_degree = {node: 0 for node in graph}
        
        # Calculate in-degrees
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        # Find nodes with no incoming edges
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Reduce in-degree of neighbors
            for neighbor in graph.get(node, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        return result
    
    def setup_environment_configs(self):
        """Setup environment-specific configurations"""
        print(f"🔧 Setting up configurations for {self.environment} environment...")
        
        if self.environment == 'colab':
            self.setup_colab_configs()
        elif self.environment == 'docker':
            self.setup_docker_configs()
        elif self.environment == 'kubernetes':
            self.setup_k8s_configs()
        else:
            self.setup_local_configs()
    
    def setup_colab_configs(self):
        """Setup Colab-specific configurations"""
        # Install ngrok if needed
        try:
            import pyngrok
        except ImportError:
            print("📦 Installing pyngrok for Colab environment...")
            subprocess.run(['pip', 'install', 'pyngrok'], check=True)
    
    def setup_docker_configs(self):
        """Setup Docker-specific configurations"""
        # Ensure Docker is available
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("⚠️  Docker not available in this environment")
    
    def setup_k8s_configs(self):
        """Setup Kubernetes-specific configurations"""
        # Ensure kubectl is available
        try:
            subprocess.run(['kubectl', 'version'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("⚠️  kubectl not available in this environment")
    
    def setup_local_configs(self):
        """Setup local environment configurations"""
        # Check for common development tools
        tools = ['npm', 'node', 'python', 'pip', 'git']
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"⚠️  {tool} not available")
    
    def start_services_sequentially(self, repo_path: str) -> Dict[str, Any]:
        """Start services in the determined order"""
        print("🚀 Starting services in sequence...")
        
        startup_results = {}
        
        for service_name in self.startup_order:
            if service_name in self.service_dependencies:
                service_data = self.service_dependencies[service_name]
                result = self.start_service(service_name, service_data, repo_path)
                startup_results[service_name] = result
                
                if result['status'] == 'success':
                    print(f"✅ {service_name} started successfully")
                else:
                    print(f"❌ {service_name} failed to start: {result.get('error', 'Unknown error')}")
        
        return startup_results
    
    def start_service(self, service_name: str, service_data: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
        """Start a specific service"""
        try:
            service_path = service_data['path']
            service_type = service_data['type']
            framework = service_data['framework']
            role = service_data['role']
            
            full_service_path = os.path.join(repo_path, service_path)
            
            if not os.path.exists(full_service_path):
                return {'status': 'error', 'error': f'Service path not found: {full_service_path}'}
            
            # Start service based on type
            if service_type == 'node':
                return self.start_node_service(service_name, full_service_path, framework, role)
            elif service_type == 'python':
                return self.start_python_service(service_name, full_service_path, framework, role)
            elif service_type == 'docker':
                return self.start_docker_service(service_name, full_service_path)
            else:
                return {'status': 'error', 'error': f'Unsupported service type: {service_type}'}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def start_node_service(self, service_name: str, service_path: str, framework: str, role: str) -> Dict[str, Any]:
        """Start a Node.js service"""
        try:
            # Install dependencies
            print(f"📦 Installing dependencies for {service_name}...")
            subprocess.run(['npm', 'install'], cwd=service_path, check=True)
            
            # Determine start command
            if framework == 'react':
                start_cmd = ['npm', 'start']
            elif framework == 'vue':
                start_cmd = ['npm', 'run', 'dev']
            elif framework == 'express':
                start_cmd = ['npm', 'start']
            else:
                start_cmd = ['npm', 'start']
            
            # Start service
            process = subprocess.Popen(
                start_cmd,
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Store process info
            self.service_processes[service_name] = {
                'process': process,
                'type': 'node',
                'path': service_path,
                'role': role
            }
            
            # Wait a bit for service to start
            time.sleep(3)
            
            return {'status': 'success', 'pid': process.pid}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def start_python_service(self, service_name: str, service_path: str, framework: str, role: str) -> Dict[str, Any]:
        """Start a Python service"""
        try:
            # Install dependencies
            print(f"📦 Installing dependencies for {service_name}...")
            
            requirements_file = os.path.join(service_path, 'requirements.txt')
            if os.path.exists(requirements_file):
                subprocess.run(['pip', 'install', '-r', 'requirements.txt'], cwd=service_path, check=True)
            
            # Determine start command
            if framework == 'django':
                start_cmd = ['python', 'manage.py', 'runserver', '0.0.0.0:8000']
            elif framework == 'flask':
                start_cmd = ['python', 'app.py']
            elif framework == 'fastapi':
                start_cmd = ['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000']
            else:
                # Try to find main file
                main_files = ['app.py', 'main.py', 'server.py', 'index.py']
                for main_file in main_files:
                    if os.path.exists(os.path.join(service_path, main_file)):
                        start_cmd = ['python', main_file]
                        break
                else:
                    return {'status': 'error', 'error': 'No main Python file found'}
            
            # Start service
            process = subprocess.Popen(
                start_cmd,
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Store process info
            self.service_processes[service_name] = {
                'process': process,
                'type': 'python',
                'path': service_path,
                'role': role
            }
            
            # Wait a bit for service to start
            time.sleep(3)
            
            return {'status': 'success', 'pid': process.pid}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def start_docker_service(self, service_name: str, service_path: str) -> Dict[str, Any]:
        """Start a Docker service"""
        try:
            # Check for docker-compose
            docker_compose_file = os.path.join(service_path, 'docker-compose.yml')
            if os.path.exists(docker_compose_file):
                subprocess.run(['docker-compose', 'up', '-d'], cwd=service_path, check=True)
            else:
                # Check for Dockerfile
                dockerfile = os.path.join(service_path, 'Dockerfile')
                if os.path.exists(dockerfile):
                    # Build and run
                    subprocess.run(['docker', 'build', '-t', service_name, '.'], cwd=service_path, check=True)
                    subprocess.run(['docker', 'run', '-d', '--name', service_name, service_name], cwd=service_path, check=True)
                else:
                    return {'status': 'error', 'error': 'No Docker configuration found'}
            
            return {'status': 'success'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def monitor_services(self) -> Dict[str, Any]:
        """Monitor running services for health"""
        print("🏥 Monitoring service health...")
        
        health_results = {}
        
        for service_name, process_info in self.service_processes.items():
            process = process_info['process']
            health_status = self.check_service_health(service_name, process_info)
            health_results[service_name] = health_status
        
        return health_results
    
    def check_service_health(self, service_name: str, process_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of a specific service"""
        process = process_info['process']
        service_type = process_info['type']
        
        # Check if process is still running
        if process.poll() is None:
            # Process is running, check if it's responding
            if service_type == 'node':
                return self.check_node_health(service_name, process_info)
            elif service_type == 'python':
                return self.check_python_health(service_name, process_info)
            else:
                return {'status': 'running', 'pid': process.pid}
        else:
            return {'status': 'stopped', 'exit_code': process.returncode}
    
    def check_node_health(self, service_name: str, process_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of Node.js service"""
        # Try to connect to the service
        try:
            import requests
            # Common Node.js ports
            ports = [3000, 3001, 8080, 4000, 5000]
            
            for port in ports:
                try:
                    response = requests.get(f'http://localhost:{port}', timeout=2)
                    if response.status_code < 500:
                        return {
                            'status': 'healthy',
                            'port': port,
                            'response_time': response.elapsed.total_seconds()
                        }
                except requests.RequestException:
                    continue
            
            return {'status': 'running', 'note': 'Service running but not responding on common ports'}
            
        except ImportError:
            return {'status': 'running', 'note': 'requests not available for health check'}
    
    def check_python_health(self, service_name: str, process_info: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of Python service"""
        try:
            import requests
            # Common Python ports
            ports = [8000, 5000, 8080, 3000]
            
            for port in ports:
                try:
                    response = requests.get(f'http://localhost:{port}', timeout=2)
                    if response.status_code < 500:
                        return {
                            'status': 'healthy',
                            'port': port,
                            'response_time': response.elapsed.total_seconds()
                        }
                except requests.RequestException:
                    continue
            
            return {'status': 'running', 'note': 'Service running but not responding on common ports'}
            
        except ImportError:
            return {'status': 'running', 'note': 'requests not available for health check'}
    
    def generate_access_urls(self) -> Dict[str, str]:
        """Generate access URLs for all services"""
        print("🔗 Generating access URLs...")
        
        access_urls = {}
        
        if self.port_manager:
            port_mappings = self.port_manager.get_port_mappings()
            
            for service_name, process_info in self.service_processes.items():
                # Find the port for this service
                for port, mapping in port_mappings.items():
                    if mapping.get('service_name') == service_name:
                        access_urls[service_name] = mapping['public_url']
                        break
                else:
                    # Default URL
                    access_urls[service_name] = f"http://localhost:3000"  # Default port
        
        return access_urls
    
    def stop_all_services(self):
        """Stop all running services"""
        print("🛑 Stopping all services...")
        
        for service_name, process_info in self.service_processes.items():
            try:
                process = process_info['process']
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {service_name}")
            except Exception as e:
                print(f"❌ Failed to stop {service_name}: {e}")

# Enhanced Orchestrator
class Orchestrator:
    """Enhanced orchestrator with autonomous service management"""
    
    def __init__(self, timeout=300):
        self.timeout = timeout
        self.service_orchestrator = AutonomousServiceOrchestrator()
        self.detection_results = {}
        self.port_manager = None
    
    def set_port_manager(self, port_manager):
        """Set the port manager for the orchestrator"""
        self.port_manager = port_manager
        self.service_orchestrator.port_manager = port_manager
    
    def run(self, repo_path: str, mode: str = 'local') -> Dict[str, Any]:
        """Main run method that orchestrates the entire workflow"""
        print("🎯 Starting intelligent workflow orchestration...")
        
        try:
            # Import required agents
            from .detection_agent import DetectionAgent
            from .requirements_agent import RequirementsAgent
            from .setup_agent import SetupAgent
            from .port_manager_agent import PortManagerAgent
            from .health_agent import HealthAgent
            
            # Initialize agents
            detection_agent = DetectionAgent()
            requirements_agent = RequirementsAgent()
            setup_agent = SetupAgent()
            port_manager_agent = PortManagerAgent()
            health_agent = HealthAgent()
            
            # Set port manager for orchestrator
            self.set_port_manager(port_manager_agent.port_manager)
            
            # Phase 1: Repository Analysis
            print("\n🔄 Phase: Repository Analysis")
            detection_results = detection_agent.detect_project_structure(repo_path)
            
            if detection_results['status'] == 'error':
                return {'status': 'error', 'error': detection_results['error']}
            
            # Phase 2: Port Management
            print("\n🔄 Phase: Port Management")
            port_results = port_manager_agent.manage_ports(repo_path)
            
            # Phase 3: Environment Assessment
            print("\n🔄 Phase: Environment Assessment")
            requirements_results = requirements_agent.assess_requirements(repo_path)
            
            # Phase 4: Setup
            print("\n🔄 Phase: Setup")
            setup_results = setup_agent.setup_project(repo_path)
            
            # Phase 5: Autonomous Service Orchestration
            print("\n🔄 Phase: Service Orchestration")
            orchestration_results = self.orchestrate(repo_path, detection_results)
            
            # Phase 6: Health Check
            print("\n🔄 Phase: Health Check")
            health_results = health_agent.check_health(repo_path)
            
            # Generate final summary
            final_result = {
                'status': 'success',
                'detection': detection_results,
                'port_management': port_results,
                'requirements': requirements_results,
                'setup': setup_results,
                'orchestration': orchestration_results,
                'health': health_results,
                'mode': mode,
                'timeout': self.timeout
            }
            
            print("\n✅ Workflow completed successfully!")
            return final_result
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'mode': mode,
                'timeout': self.timeout
            }
    
    def orchestrate(self, repo_path: str, detection_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced orchestration with autonomous service management"""
        print("🎯 Starting intelligent workflow orchestration...")
        
        self.detection_results = detection_results
        
        try:
            # Run autonomous service orchestration
            orchestration_results = self.service_orchestrator.orchestrate_services(
                repo_path, 
                detection_results, 
                self.port_manager
            )
            
            if orchestration_results['status'] == 'success':
                print("✅ Service orchestration completed successfully!")
                print(f"   🚀 Started {orchestration_results['services_started']} services")
                print(f"   🌍 Environment: {orchestration_results['environment']}")
                
                # Print access URLs
                if orchestration_results.get('access_urls'):
                    print("\n🔗 Service Access URLs:")
                    for service, url in orchestration_results['access_urls'].items():
                        print(f"   {service}: {url}")
            
            return orchestration_results
            
        except Exception as e:
            print(f"❌ Orchestration failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def cleanup(self):
        """Cleanup all resources"""
        self.service_orchestrator.stop_all_services()
