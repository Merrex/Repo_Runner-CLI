"""
Health check functionality for running services.
"""

import requests
import time
import socket
from typing import Dict, Any, Optional
from .logger import get_logger


class HealthChecker:
    """Performs health checks on running services."""
    
    def __init__(self, path, config: Dict = None):
        self.path = path
        self.config = config or {}
        self.logger = get_logger()
    
    def check_all(self, services: Dict[str, Any]) -> bool:
        """Check health of all services."""
        all_healthy = True
        
        for service_name, service_info in services.items():
            try:
                healthy = self.check_service(service_name, service_info)
                service_info['healthy'] = healthy
                
                if healthy:
                    self.logger.info(f"✅ {service_name} is healthy")
                else:
                    self.logger.warning(f"❌ {service_name} is not healthy")
                    all_healthy = False
                    
            except Exception as e:
                self.logger.error(f"❌ Health check failed for {service_name}: {e}")
                service_info['healthy'] = False
                all_healthy = False
        
        return all_healthy
    
    def check_service(self, service_name: str, service_info: Dict[str, Any]) -> bool:
        """Check health of a single service."""
        service_type = service_info.get('type', 'web')
        
        if service_type == 'web':
            return self._check_web_service(service_info)
        elif service_type == 'database':
            return self._check_database_service(service_info)
        elif service_type == 'api':
            return self._check_api_service(service_info)
        else:
            return self._check_generic_service(service_info)
    
    def _check_web_service(self, service_info: Dict[str, Any]) -> bool:
        """Check web service health."""
        url = service_info.get('url')
        if not url:
            return False
        
        try:
            # Try to connect to the service
            response = requests.get(url, timeout=10)
            return response.status_code < 500
        except requests.exceptions.RequestException:
            # If HTTP fails, try basic port check
            return self._check_port(service_info)
    
    def _check_api_service(self, service_info: Dict[str, Any]) -> bool:
        """Check API service health."""
        url = service_info.get('url')
        if not url:
            return False
        
        # Try common health check endpoints
        health_endpoints = ['/health', '/healthz', '/status', '/ping', '/api/health']
        
        for endpoint in health_endpoints:
            try:
                health_url = url.rstrip('/') + endpoint
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    return True
            except:
                continue
        
        # Fallback to basic connectivity check
        return self._check_web_service(service_info)
    
    def _check_database_service(self, service_info: Dict[str, Any]) -> bool:
        """Check database service health."""
        # This would need database-specific connection logic
        return self._check_port(service_info)
    
    def _check_generic_service(self, service_info: Dict[str, Any]) -> bool:
        """Check generic service health."""
        return self._check_port(service_info)
    
    def _check_port(self, service_info: Dict[str, Any]) -> bool:
        """Check if service port is accessible."""
        port = service_info.get('port')
        host = service_info.get('host', 'localhost')
        
        if not port:
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def wait_for_services(self, services: Dict[str, Any], timeout: int = 60) -> bool:
        """Wait for services to become healthy."""
        self.logger.info(f"Waiting for services to become healthy (timeout: {timeout}s)")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.check_all(services):
                self.logger.info("✅ All services are healthy")
                return True
            
            time.sleep(2)
        
        self.logger.warning("❌ Timeout waiting for services to become healthy")
        return False
    
    def get_service_status(self, services: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed status of all services."""
        status = {}
        
        for service_name, service_info in services.items():
            service_status = {
                'name': service_name,
                'type': service_info.get('type', 'unknown'),
                'url': service_info.get('url'),
                'port': service_info.get('port'),
                'healthy': service_info.get('healthy', False),
                'last_check': time.time()
            }
            
            # Add additional checks
            if service_info.get('url'):
                service_status['response_time'] = self._measure_response_time(service_info['url'])
            
            status[service_name] = service_status
        
        return status
    
    def _measure_response_time(self, url: str) -> Optional[float]:
        """Measure response time for a URL."""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            end_time = time.time()
            
            if response.status_code < 500:
                return round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        except:
            pass
        
        return None