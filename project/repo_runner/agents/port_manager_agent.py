import socket
import subprocess
import psutil
import os
import time
from typing import Dict, List, Optional, Tuple

class PortManagerAgent:
    """Manages port allocation, checking availability, and freeing occupied ports."""
    
    def __init__(self):
        # Default port mappings for common services
        self.default_ports = {
            'backend': 8000,
            'frontend': 3000,
            'database': 5432,
            'redis': 6379,
            'mongodb': 27017,
            'elasticsearch': 9200,
            'kibana': 5601,
            'postgres': 5432,
            'mysql': 3306,
            'nginx': 80,
            'apache': 8080
        }
        
        # Port ranges for dynamic allocation
        self.backend_port_range = (8000, 8100)
        self.frontend_port_range = (3000, 3100)
        self.database_port_range = (5432, 5442)
    
    def check_port_availability(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False
    
    def find_free_port(self, start_port: int, end_port: int) -> Optional[int]:
        """Find a free port in the given range."""
        for port in range(start_port, end_port + 1):
            if self.check_port_availability(port):
                return port
        return None
    
    def get_process_using_port(self, port: int) -> Optional[Dict]:
        """Get information about the process using a specific port."""
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port:
                    if conn.pid:
                        process = psutil.Process(conn.pid)
                        return {
                            'pid': conn.pid,
                            'name': process.name(),
                            'cmdline': ' '.join(process.cmdline()),
                            'status': conn.status
                        }
        except Exception:
            pass
        return None
    
    def kill_process_on_port(self, port: int) -> bool:
        """Kill the process using a specific port."""
        process_info = self.get_process_using_port(port)
        if process_info:
            try:
                process = psutil.Process(process_info['pid'])
                process.terminate()
                time.sleep(1)
                if process.is_running():
                    process.kill()
                return True
            except Exception:
                return False
        return False
    
    def allocate_ports_for_services(self, services: List[Dict]) -> Dict[str, int]:
        """Allocate appropriate ports for detected services."""
        allocated_ports = {}
        
        for service in services:
            service_type = service.get('type')
            service_role = service.get('role', 'unknown')
            
            if service_type == 'python' and service_role == 'backend':
                port = self._allocate_backend_port()
                allocated_ports['backend'] = port
                
            elif service_type == 'node' and service_role == 'frontend':
                port = self._allocate_frontend_port()
                allocated_ports['frontend'] = port
                
            elif service_type == 'docker' and service_role == 'db':
                port = self._allocate_database_port()
                allocated_ports['database'] = port
        
        return allocated_ports
    
    def _allocate_backend_port(self) -> int:
        """Allocate a port for backend services."""
        # Try default backend port first
        if self.check_port_availability(self.default_ports['backend']):
            return self.default_ports['backend']
        
        # Find free port in backend range
        free_port = self.find_free_port(*self.backend_port_range)
        if free_port:
            return free_port
        
        # If no free port, try to free the default port
        if self.kill_process_on_port(self.default_ports['backend']):
            return self.default_ports['backend']
        
        # Last resort: find any free port
        return self.find_free_port(8000, 9000) or 8000
    
    def _allocate_frontend_port(self) -> int:
        """Allocate a port for frontend services."""
        # Try default frontend port first
        if self.check_port_availability(self.default_ports['frontend']):
            return self.default_ports['frontend']
        
        # Find free port in frontend range
        free_port = self.find_free_port(*self.frontend_port_range)
        if free_port:
            return free_port
        
        # If no free port, try to free the default port
        if self.kill_process_on_port(self.default_ports['frontend']):
            return self.default_ports['frontend']
        
        # Last resort: find any free port
        return self.find_free_port(3000, 4000) or 3000
    
    def _allocate_database_port(self) -> int:
        """Allocate a port for database services."""
        # Try default database port first
        if self.check_port_availability(self.default_ports['database']):
            return self.default_ports['database']
        
        # Find free port in database range
        free_port = self.find_free_port(*self.database_port_range)
        if free_port:
            return free_port
        
        # If no free port, try to free the default port
        if self.kill_process_on_port(self.default_ports['database']):
            return self.default_ports['database']
        
        # Last resort: find any free port
        return self.find_free_port(5432, 5532) or 5432
    
    def check_service_ports(self, services: List[Dict]) -> Dict[str, Dict]:
        """Check the status of all service ports."""
        port_status = {}
        
        for service in services:
            service_type = service.get('type')
            service_role = service.get('role', 'unknown')
            
            if service_type == 'python' and service_role == 'backend':
                port = self.default_ports['backend']
                status = self._check_service_port(port, 'Backend')
                port_status['backend'] = status
                
            elif service_type == 'node' and service_role == 'frontend':
                port = self.default_ports['frontend']
                status = self._check_service_port(port, 'Frontend')
                port_status['frontend'] = status
                
            elif service_type == 'docker' and service_role == 'db':
                port = self.default_ports['database']
                status = self._check_service_port(port, 'Database')
                port_status['database'] = status
        
        return port_status
    
    def _check_service_port(self, port: int, service_name: str) -> Dict:
        """Check the status of a specific service port."""
        is_available = self.check_port_availability(port)
        process_info = self.get_process_using_port(port)
        
        return {
            'port': port,
            'available': is_available,
            'service_name': service_name,
            'process_info': process_info,
            'status': 'available' if is_available else 'occupied'
        }
    
    def free_occupied_ports(self, services: List[Dict]) -> Dict[str, bool]:
        """Free ports that are occupied by other processes."""
        freed_ports = {}
        
        for service in services:
            service_type = service.get('type')
            service_role = service.get('role', 'unknown')
            
            if service_type == 'python' and service_role == 'backend':
                port = self.default_ports['backend']
                freed_ports['backend'] = self.kill_process_on_port(port)
                
            elif service_type == 'node' and service_role == 'frontend':
                port = self.default_ports['frontend']
                freed_ports['frontend'] = self.kill_process_on_port(port)
                
            elif service_type == 'docker' and service_role == 'db':
                port = self.default_ports['database']
                freed_ports['database'] = self.kill_process_on_port(port)
        
        return freed_ports
    
    def get_port_configuration(self, services: List[Dict]) -> Dict:
        """Get complete port configuration for all services."""
        # Check current port status
        port_status = self.check_service_ports(services)
        
        # Free occupied ports if needed
        freed_ports = self.free_occupied_ports(services)
        
        # Allocate ports
        allocated_ports = self.allocate_ports_for_services(services)
        
        return {
            'allocated_ports': allocated_ports,
            'port_status': port_status,
            'freed_ports': freed_ports,
            'recommendations': self._generate_port_recommendations(port_status, freed_ports)
        }
    
    def _generate_port_recommendations(self, port_status: Dict, freed_ports: Dict) -> List[str]:
        """Generate recommendations based on port status."""
        recommendations = []
        
        for service, status in port_status.items():
            if not status['available'] and freed_ports.get(service):
                recommendations.append(f"Freed port {status['port']} for {service}")
            elif not status['available']:
                recommendations.append(f"Port {status['port']} is occupied by {status['process_info']['name'] if status['process_info'] else 'unknown process'}")
            else:
                recommendations.append(f"Port {status['port']} is available for {service}")
        
        return recommendations
    
    def validate_port_configuration(self, allocated_ports: Dict[str, int]) -> Tuple[bool, List[str]]:
        """Validate that the port configuration is valid."""
        errors = []
        used_ports = set()
        
        for service, port in allocated_ports.items():
            if port in used_ports:
                errors.append(f"Port {port} is allocated to multiple services")
            elif not self.check_port_availability(port):
                errors.append(f"Port {port} for {service} is not available")
            else:
                used_ports.add(port)
        
        return len(errors) == 0, errors
