import requests
import subprocess
import json
import time
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm

class HealthAgent:
    def check(self, run_status):
        """Check the health of the running service(s) using LLM."""
        if not run_status or run_status.get('status') == 'not implemented':
            return {"ok": False, "errors": ["No running services to check"]}
        
        health_results = {
            'ok': True,
            'services': {},
            'errors': [],
            'warnings': [],
            'urls': run_status.get('urls', [])
        }
        
        # Check each service
        for service in run_status.get('started_services', []):
            service_health = self._check_service_health(service, run_status)
            health_results['services'][service] = service_health
            
            if not service_health.get('healthy', False):
                health_results['ok'] = False
                health_results['errors'].extend(service_health.get('errors', []))
        
        # Check URLs if available
        if run_status.get('urls'):
            url_health = self._check_urls(run_status['urls'])
            health_results.update(url_health)
        
        # Use LLM to analyze overall health
        analysis = self._analyze_health_status(health_results, run_status)
        health_results['analysis'] = analysis
        
        return health_results
    
    def _check_service_health(self, service, run_status):
        """Check health of a specific service."""
        try:
            if service == 'docker':
                return self._check_docker_health(run_status)
            elif service == 'python':
                return self._check_python_health(run_status)
            elif service == 'node':
                return self._check_node_health(run_status)
            else:
                return self._check_generic_health(service, run_status)
        except Exception as e:
            return {
                'healthy': False,
                'errors': [f"Health check failed for {service}: {e}"]
            }
    
    def _check_docker_health(self, run_status):
        """Check Docker service health."""
        try:
            # Check if Docker containers are running
            result = subprocess.run(
                ['docker', 'ps'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and 'Up' in result.stdout:
                return {
                    'healthy': True,
                    'status': 'running',
                    'containers': result.stdout.strip()
                }
            else:
                return {
                    'healthy': False,
                    'status': 'not_running',
                    'errors': ['Docker containers not running']
                }
        except Exception as e:
            return {
                'healthy': False,
                'errors': [f"Docker health check failed: {e}"]
            }
    
    def _check_python_health(self, run_status):
        """Check Python service health."""
        try:
            # Check if Python process is running
            processes = run_status.get('processes', [])
            python_processes = [p for p in processes if p.get('type') == 'python']
            
            if python_processes:
                pid = python_processes[0].get('pid')
                if pid:
                    # Check if process is still running
                    result = subprocess.run(
                        ['ps', '-p', str(pid)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        return {
                            'healthy': True,
                            'status': 'running',
                            'pid': pid
                        }
            
            return {
                'healthy': False,
                'status': 'not_running',
                'errors': ['Python process not found']
            }
        except Exception as e:
            return {
                'healthy': False,
                'errors': [f"Python health check failed: {e}"]
            }
    
    def _check_node_health(self, run_status):
        """Check Node.js service health."""
        try:
            # Check if Node.js process is running
            processes = run_status.get('processes', [])
            node_processes = [p for p in processes if p.get('type') == 'node']
            
            if node_processes:
                pid = node_processes[0].get('pid')
                if pid:
                    # Check if process is still running
                    result = subprocess.run(
                        ['ps', '-p', str(pid)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        return {
                            'healthy': True,
                            'status': 'running',
                            'pid': pid
                        }
            
            return {
                'healthy': False,
                'status': 'not_running',
                'errors': ['Node.js process not found']
            }
        except Exception as e:
            return {
                'healthy': False,
                'errors': [f"Node.js health check failed: {e}"]
            }
    
    def _check_generic_health(self, service, run_status):
        """Check generic service health."""
        try:
            # Check if any process is running
            processes = run_status.get('processes', [])
            service_processes = [p for p in processes if p.get('type') == service]
            
            if service_processes:
                pid = service_processes[0].get('pid')
                if pid:
                    result = subprocess.run(
                        ['ps', '-p', str(pid)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        return {
                            'healthy': True,
                            'status': 'running',
                            'pid': pid
                        }
            
            return {
                'healthy': False,
                'status': 'not_running',
                'errors': [f'{service} process not found']
            }
        except Exception as e:
            return {
                'healthy': False,
                'errors': [f"{service} health check failed: {e}"]
            }
    
    def _check_urls(self, urls):
        """Check if URLs are responding."""
        url_results = {
            'url_checks': {},
            'url_errors': []
        }
        
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                url_results['url_checks'][url] = {
                    'status_code': response.status_code,
                    'healthy': response.status_code < 400,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                url_results['url_checks'][url] = {
                    'status_code': None,
                    'healthy': False,
                    'error': str(e)
                }
                url_results['url_errors'].append(f"{url}: {e}")
        
        return url_results
    
    def _analyze_health_status(self, health_results, run_status):
        """Use LLM to analyze health status and suggest fixes."""
        try:
            prompt = f"""
            Analyze the health status of this application:
            
            Health Results: {json.dumps(health_results, indent=2)}
            Run Status: {json.dumps(run_status, indent=2)}
            
            Provide:
            1. Overall health assessment
            2. Specific issues found
            3. Recommended fixes
            4. Next steps
            
            Format as JSON with keys: assessment, issues, fixes, next_steps
            """
            
            analysis = generate_code_with_llm(prompt, agent_name='health_agent')
            
            try:
                return json.loads(analysis)
            except json.JSONDecodeError:
                return {
                    'assessment': 'Health analysis completed',
                    'issues': health_results.get('errors', []),
                    'fixes': 'Manual review required',
                    'next_steps': 'Check logs and restart services if needed'
                }
                
        except Exception as e:
            return {
                'assessment': 'Health analysis failed',
                'issues': [f"Analysis error: {e}"],
                'fixes': 'Manual intervention required',
                'next_steps': 'Check system logs'
            }
    
    def check_services(self, structure):
        """Check if each detected service is running."""
        results = []
        for svc in structure.get('services', []):
            if svc['type'] == 'python':
                try:
                    r = requests.get('http://localhost:8000')
                    results.append({'service': svc, 'status': r.status_code})
                except Exception as e:
                    results.append({'service': svc, 'status': 'down', 'error': str(e)})
            elif svc['type'] == 'node':
                try:
                    r = requests.get('http://localhost:3000')
                    results.append({'service': svc, 'status': r.status_code})
                except Exception as e:
                    results.append({'service': svc, 'status': 'down', 'error': str(e)})
        return results 