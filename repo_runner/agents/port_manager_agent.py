import socket
import subprocess
import psutil
import os
import sys
import time
from typing import Dict, List, Optional, Tuple
import requests
import json
from pathlib import Path
from ..config_manager import config_manager
from .config_agent import ConfigAgent
from .dependency_agent import DependencyAgent

class EnvironmentAwarePortManager:
    """
    Enhanced port manager that's aware of different environments (Colab, local, Docker, K8s).
    Uses DependencyAgent for all dependency management (agentic OOP pattern).
    """
    
    def __init__(self):
        self.environment = self.detect_environment()
        self.port_mappings = {}
        self.tunnels = {}
        self.config_agent = ConfigAgent()  # Agentic config file manager
        self.dependency_agent = DependencyAgent()
        self.dependency_agent.ensure_packages(['pyngrok', 'requests'], upgrade=False)
        print(f"🔍 Detected environment: {self.environment}")
    
    def detect_environment(self) -> str:
        """Detect the current environment"""
        # Check for Colab
        if 'COLAB_GPU' in os.environ or 'COLAB_TPU' in os.environ:
            return 'colab'
        
        # Check for Google Cloud
        if 'GOOGLE_CLOUD_PROJECT' in os.environ:
            return 'gcp'
        
        # Check for Kubernetes
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            return 'kubernetes'
        
        # Check for Docker
        if os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup') and 'docker' in open('/proc/1/cgroup').read():
            return 'docker'
        
        # Check for AWS
        if 'AWS_EXECUTION_ENV' in os.environ:
            return 'aws'
        
        # Default to local
        return 'local'
    
    def setup_port_access(self, port: int, service_name: str = None) -> Dict[str, str]:
        """Setup port access based on environment"""
        print(f"🔌 Setting up port access for port {port} in {self.environment} environment")
        
        if self.environment == 'colab':
            return self.setup_colab_access(port, service_name)
        elif self.environment == 'kubernetes':
            return self.setup_k8s_access(port, service_name)
        elif self.environment == 'docker':
            return self.setup_docker_access(port, service_name)
        elif self.environment == 'gcp':
            return self.setup_gcp_access(port, service_name)
        else:
            return self.setup_local_access(port, service_name)
    
    def setup_colab_access(self, port: int, service_name: str = None) -> Dict[str, str]:
        """Setup ngrok tunnel for Colab environment with proper authentication"""
        try:
            # Install pyngrok if not available
            try:
                from pyngrok import ngrok
            except ImportError:
                print("📦 Installing pyngrok for Colab environment...")
                subprocess.run([sys.executable, "-m", "pip", "install", "pyngrok"], check=True)
                from pyngrok import ngrok
            
            # Cleanup existing tunnels to prevent hitting limits
            try:
                ngrok.kill()
                print("🧹 Cleaned up existing ngrok tunnels")
            except Exception as e:
                print(f"⚠️ Failed to cleanup ngrok tunnels: {e}")
            
            # Get ngrok configuration
            ngrok_config = config_manager.get_integration_config('ngrok')
            auth_token = ngrok_config.get('auth_token')
            
            # Use ConfigAgent (child of FileAgent) for ngrok config creation
            multiplex_ports = {service_name or f"service_{port}": port}
            config_path = os.path.expanduser("~/.config/ngrok/ngrok.yml")
            if auth_token:
                self.config_agent.create_ngrok_config(auth_token, multiplex_ports, config_path)
                os.environ['NGROK_CONFIG'] = config_path
                print(f"✅ Ngrok multiplex config written via ConfigAgent: {config_path}")
            else:
                print("⚠️ No NGROK_AUTH_TOKEN found - using free tier (limited)")
                print("💡 Get free token at: https://dashboard.ngrok.com/get-started/your-authtoken")
            
            # Start ngrok agent with config (multiplexing)
            ngrok_process = subprocess.Popen(['ngrok', 'start', '--all'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.tunnels[port] = ngrok_process  # Store process, not tunnel object
            
            # Wait for ngrok API to be ready (retry loop)
            public_url = None
            api_ready = False
            for _ in range(15):  # Wait up to ~15 seconds
                try:
                    tunnels_info = requests.get('http://localhost:4040/api/tunnels').json()['tunnels']
                    api_ready = True
                    for tunnel in tunnels_info:
                        if str(port) in tunnel['config']['addr']:
                            public_url = tunnel['public_url']
                            break
                    break
                except Exception:
                    time.sleep(1)
            if not api_ready:
                print(f"❌ Ngrok API not ready after waiting, using local URL for port {port}")
                public_url = f"http://localhost:{port}"
            elif not public_url:
                public_url = f"http://localhost:{port}"
            
            self.port_mappings[port] = {
                'local_url': f"http://localhost:{port}",
                'public_url': public_url,
                'environment': 'colab',
                'service_name': service_name
            }
            print(f"✅ Colab access setup: {public_url}")
            return self.port_mappings[port]
        except Exception as e:
            print(f"❌ Failed to setup Colab access: {e}")
            if "authentication failed" in str(e).lower():
                print("💡 To fix ngrok authentication:")
                print("   1. Get free token: https://dashboard.ngrok.com/get-started/your-authtoken")
                print("   2. Add to .env file: NGROK_AUTH_TOKEN=your_token_here")
                print("   3. Or set environment: export NGROK_AUTH_TOKEN=your_token_here")
            return self.setup_local_access(port, service_name)
    
    def setup_k8s_access(self, port: int, service_name: str = None) -> Dict[str, str]:
        """Setup Kubernetes service access"""
        try:
            # Create Kubernetes service
            service_name = service_name or f"repo-runner-service-{port}"
            
            # Create service YAML
            service_yaml = f"""
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
spec:
  selector:
    app: repo-runner
  ports:
  - protocol: TCP
    port: {port}
    targetPort: {port}
  type: LoadBalancer
"""
            
            # Apply service
            with open(f"/tmp/{service_name}.yaml", 'w') as f:
                f.write(service_yaml)
            
            subprocess.run(['kubectl', 'apply', '-f', f"/tmp/{service_name}.yaml"], check=True)
            
            # Get external IP
            time.sleep(5)  # Wait for service to be ready
            result = subprocess.run(['kubectl', 'get', 'service', service_name, '-o', 'jsonpath={.status.loadBalancer.ingress[0].ip}'], 
                                  capture_output=True, text=True)
            
            external_ip = result.stdout.strip()
            if external_ip:
                public_url = f"http://{external_ip}:{port}"
            else:
                public_url = f"http://{service_name}.default.svc.cluster.local:{port}"
            
            self.port_mappings[port] = {
                'local_url': f"http://localhost:{port}",
                'public_url': public_url,
                'environment': 'kubernetes',
                'service_name': service_name
            }
            
            print(f"✅ Kubernetes access setup: {public_url}")
            return self.port_mappings[port]
            
        except Exception as e:
            print(f"❌ Failed to setup Kubernetes access: {e}")
            return self.setup_local_access(port, service_name)
    
    def setup_docker_access(self, port: int, service_name: str = None) -> Dict[str, str]:
        """Setup Docker port mapping"""
        try:
            # Get container IP
            result = subprocess.run(['hostname', '-i'], capture_output=True, text=True)
            container_ip = result.stdout.strip()
            
            # Map port to host
            host_port = self.find_available_port(port)
            subprocess.run(['docker', 'run', '-d', '-p', f"{host_port}:{port}", '--name', f"repo-runner-{port}"], check=True)
            
            public_url = f"http://localhost:{host_port}"
            
            self.port_mappings[port] = {
                'local_url': f"http://localhost:{port}",
                'public_url': public_url,
                'environment': 'docker',
                'service_name': service_name
            }
            
            print(f"✅ Docker access setup: {public_url}")
            return self.port_mappings[port]
            
        except Exception as e:
            print(f"❌ Failed to setup Docker access: {e}")
            return self.setup_local_access(port, service_name)
    
    def setup_gcp_access(self, port: int, service_name: str = None) -> Dict[str, str]:
        """Setup Google Cloud access"""
        try:
            # Use Cloud Run or App Engine for GCP
            service_name = service_name or f"repo-runner-{port}"
            
            # For now, return local access (GCP setup requires more complex configuration)
            return self.setup_local_access(port, service_name)
            
        except Exception as e:
            print(f"❌ Failed to setup GCP access: {e}")
            return self.setup_local_access(port, service_name)
    
    def setup_local_access(self, port: int, service_name: str = None) -> Dict[str, str]:
        """Setup local access"""
        local_url = f"http://localhost:{port}"
        
        self.port_mappings[port] = {
            'local_url': local_url,
            'public_url': local_url,
            'environment': 'local',
            'service_name': service_name
        }
        
        print(f"✅ Local access setup: {local_url}")
        return self.port_mappings[port]
    
    def find_available_port(self, preferred_port: int) -> int:
        """Find an available port starting from preferred_port"""
        port = preferred_port
        while port < preferred_port + 100:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                port += 1
        return preferred_port
    
    def cleanup_tunnels(self):
        """Cleanup all tunnels (terminate ngrok processes)"""
        for port, tunnel in self.tunnels.items():
            try:
                # If tunnel is a Popen process, terminate it
                if hasattr(tunnel, 'terminate'):
                    tunnel.terminate()
                    tunnel.wait(timeout=5)
                    print(f"🔌 Terminated ngrok process for port {port}")
                else:
                    print(f"⚠️ Tunnel object for port {port} is not a process, skipping terminate.")
            except Exception as e:
                print(f"❌ Failed to terminate tunnel for port {port}: {e}")
        self.tunnels.clear()
    
    def get_port_mappings(self) -> Dict[int, Dict[str, str]]:
        """Get all port mappings"""
        return self.port_mappings
    
    def health_check_port(self, port: int) -> bool:
        """Check if a port is accessible"""
        try:
            mapping = self.port_mappings.get(port)
            if not mapping:
                return False
            
            url = mapping['public_url']
            response = requests.get(url, timeout=5)
            return response.status_code < 500
        except Exception:
            return False

# Enhanced Port Manager Agent
class PortManagerAgent:
    """Enhanced port manager agent with environment awareness"""
    
    def __init__(self):
        self.port_manager = EnvironmentAwarePortManager()
        self.managed_ports = {}
    
    def manage_ports(self, repo_path: str) -> Dict[str, any]:
        """Enhanced port management with environment awareness"""
        print("🔌 Managing port allocation and availability...")
        
        try:
            # Detect services that need ports
            services = self.detect_services_needing_ports(repo_path)
            
            if not services:
                print("ℹ️ No services detected, skipping port management")
                return {'status': 'no_services', 'message': 'No services detected'}
            
            # Setup port access for each service
            port_configs = {}
            for service in services:
                port_config = self.port_manager.setup_port_access(
                    service['port'], 
                    service['name']
                )
                port_configs[service['name']] = port_config
                self.managed_ports[service['port']] = port_config
            
            print(f"✅ Port management completed for {len(services)} services")
            return {
                'status': 'success',
                'services': port_configs,
                'environment': self.port_manager.environment
            }
            
        except Exception as e:
            print(f"❌ Port management failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def detect_services_needing_ports(self, repo_path: str) -> List[Dict]:
        """Detect services that need port management"""
        services = []
        
        # Common port patterns
        port_patterns = {
            'backend': [8000, 5000, 3001, 8080],
            'frontend': [3000, 3001, 8080, 4000],
            'database': [5432, 3306, 27017, 6379],
            'redis': [6379],
            'elasticsearch': [9200],
            'kafka': [9092],
            'nginx': [80, 443]
        }
        
        # Scan for configuration files
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file in ['package.json', 'docker-compose.yml', 'docker-compose.yaml', 'dockerfile', 'Dockerfile']:
                    # Analyze file to detect ports
                    file_path = os.path.join(root, file)
                    detected_ports = self.analyze_config_file(file_path)
                    
                    for port_info in detected_ports:
                        service_name = port_info.get('service', 'unknown')
                        port = port_info.get('port')
                        
                        if port:
                            services.append({
                                'name': service_name,
                                'port': port,
                                'config_file': file_path
                            })
        
        return services
    
    def analyze_config_file(self, file_path: str) -> List[Dict]:
        """Analyze configuration file to detect ports"""
        ports = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract port information based on file type
            if file_path.endswith('package.json'):
                ports.extend(self.extract_ports_from_package_json(content))
            elif file_path.endswith(('.yml', '.yaml')):
                ports.extend(self.extract_ports_from_yaml(content))
            elif file_path.endswith('dockerfile') or file_path.endswith('Dockerfile'):
                ports.extend(self.extract_ports_from_dockerfile(content))
                
        except Exception as e:
            print(f"❌ Failed to analyze {file_path}: {e}")
        
        return ports
    
    def extract_ports_from_package_json(self, content: str) -> List[Dict]:
        """Extract ports from package.json"""
        ports = []
        try:
            import json
            data = json.loads(content)
            
            # Check for start scripts
            scripts = data.get('scripts', {})
            for script_name, script in scripts.items():
                if 'start' in script_name.lower():
                    # Look for port in script
                    import re
                    port_match = re.search(r'--port\s+(\d+)', script)
                    if port_match:
                        ports.append({
                            'service': data.get('name', 'node-app'),
                            'port': int(port_match.group(1))
                        })
            
            # Default ports for common frameworks
            if 'react' in content.lower():
                ports.append({'service': 'react-app', 'port': 3000})
            elif 'vue' in content.lower():
                ports.append({'service': 'vue-app', 'port': 8080})
            elif 'express' in content.lower():
                ports.append({'service': 'express-app', 'port': 3000})
                
        except Exception as e:
            print(f"❌ Failed to parse package.json: {e}")
        
        return ports
    
    def extract_ports_from_yaml(self, content: str) -> List[Dict]:
        """Extract ports from YAML files"""
        ports = []
        try:
            import yaml
            data = yaml.safe_load(content)
            
            # Handle docker-compose files
            if 'services' in data:
                for service_name, service_config in data['services'].items():
                    if 'ports' in service_config:
                        for port_mapping in service_config['ports']:
                            if isinstance(port_mapping, str):
                                # Format: "3000:3000"
                                host_port, container_port = port_mapping.split(':')
                                ports.append({
                                    'service': service_name,
                                    'port': int(container_port)
                                })
                            elif isinstance(port_mapping, dict):
                                ports.append({
                                    'service': service_name,
                                    'port': port_mapping.get('target', 3000)
                                })
                                
        except Exception as e:
            print(f"❌ Failed to parse YAML: {e}")
        
        return ports
    
    def extract_ports_from_dockerfile(self, content: str) -> List[Dict]:
        """Extract ports from Dockerfile"""
        ports = []
        try:
            import re
            # Look for EXPOSE directives
            expose_matches = re.findall(r'EXPOSE\s+(\d+)', content, re.IGNORECASE)
            for port in expose_matches:
                ports.append({
                    'service': 'docker-service',
                    'port': int(port)
                })
                
        except Exception as e:
            print(f"❌ Failed to parse Dockerfile: {e}")
        
        return ports
    
    def cleanup(self):
        """Cleanup all managed ports"""
        self.port_manager.cleanup_tunnels()
        print("🧹 Port management cleanup completed")
