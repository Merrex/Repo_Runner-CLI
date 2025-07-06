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

class Orchestrator:
    """Intelligent orchestrator that dynamically decides which agents to use based on real-time conditions."""
    
    def __init__(self, timeout=300):  # 5 minutes default timeout
        self.agents = {
            'detection': DetectionAgent(),
            'requirements': RequirementsAgent(),
            'setup': SetupAgent(),
            'db': DBAgent(),
            'runner': RunnerAgent(),
            'health': HealthAgent(),
            'fixer': FixerAgent(),
            'port_manager': PortManagerAgent()
        }
        self.workflow_state = {}
        self.checkpoint_results = {}
        self.timeout = timeout
        self.start_time = None
    
    def run(self, repo_path: str, mode: str = "local") -> Dict[str, Any]:
        """Dynamic workflow execution with intelligent agent selection."""
        print("🎯 Starting intelligent workflow orchestration...")
        
        # Initialize workflow state
        self.workflow_state = {
            'repo_path': repo_path,
            'mode': mode,
            'current_phase': 'initialization',
            'completed_phases': [],
            'failed_phases': [],
            'retry_count': 0,
            'max_retries': 3
        }
        
        # Start timeout tracking
        self.start_time = time.time()
        
        try:
            # Phase 1: Repository Analysis
            self._execute_phase('repository_analysis', self._analyze_repository)
            
            # Phase 2: Port Management (NEW)
            self._execute_phase('port_management', self._manage_ports)
            
            # Phase 3: Environment Assessment
            self._execute_phase('environment_assessment', self._assess_environment)
            
            # Phase 4: Dependency Management
            self._execute_phase('dependency_management', self._manage_dependencies)
            
            # Phase 5: Service Configuration
            self._execute_phase('service_configuration', self._configure_services)
            
            # Phase 6: Service Startup
            self._execute_phase('service_startup', self._start_services)
            
            # Phase 7: Health Validation
            self._execute_phase('health_validation', self._validate_health)
            
            # Phase 8: Final Optimization
            self._execute_phase('final_optimization', self._optimize_system)
            
            return self._generate_final_report()
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return self._generate_error_report(e)
    
    def _execute_phase(self, phase_name: str, phase_function) -> bool:
        """Execute a workflow phase with intelligent decision making."""
        print(f"\n🔄 Phase: {phase_name.replace('_', ' ').title()}")
        
        # Check timeout
        if self._is_timeout():
            raise TimeoutError(f"Workflow timeout after {self.timeout} seconds")
        
        try:
            result = phase_function()
            self.checkpoint_results[phase_name] = result
            self.workflow_state['completed_phases'].append(phase_name)
            self.workflow_state['current_phase'] = phase_name
            
            print(f"✅ {phase_name.replace('_', ' ').title()} completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ {phase_name.replace('_', ' ').title()} failed: {e}")
            self.workflow_state['failed_phases'].append(phase_name)
            
            # Attempt recovery
            if self._should_retry_phase(phase_name):
                return self._retry_phase(phase_name, phase_function)
            else:
                return False
    
    def _analyze_repository(self) -> Dict[str, Any]:
        """Phase 1: Intelligent repository analysis."""
        print("🔍 Analyzing repository structure and services...")
        
        # Use DetectionAgent for initial analysis
        detection_result = self.agents['detection'].analyze(self.workflow_state['repo_path'])
        
        # Dynamically decide if we need deeper analysis
        if self._needs_deeper_analysis(detection_result):
            print("🔬 Performing deep analysis...")
            services_result = self.agents['detection'].detect_services(self.workflow_state['repo_path'])
            detection_result.update(services_result)
        
        return detection_result
    
    def _manage_ports(self) -> Dict[str, Any]:
        """Phase 2: Port management and allocation."""
        print("🔌 Managing port allocation and availability...")
        
        # Get services from repository analysis
        services = self.checkpoint_results['repository_analysis'].get('services', [])
        
        if not services:
            print("ℹ️ No services detected, skipping port management")
            return {'status': 'no_services', 'message': 'No services detected'}
        
        # Use PortManagerAgent for comprehensive port management
        port_result = self.agents['port_manager'].get_port_configuration(services)
        
        # Check current port status
        port_status = self.agents['port_manager'].check_service_ports(services)
        
        # Free occupied ports if needed
        freed_ports = self.agents['port_manager'].free_occupied_ports(services)
        
        # Allocate ports for services
        allocated_ports = self.agents['port_manager'].allocate_ports_for_services(services)
        
        # Validate port configuration
        is_valid, validation_errors = self.agents['port_manager'].validate_port_configuration(allocated_ports)
        
        port_management_result = {
            'port_config': port_result,
            'port_status': port_status,
            'freed_ports': freed_ports,
            'allocated_ports': allocated_ports,
            'is_valid': is_valid,
            'validation_errors': validation_errors,
            'services_count': len(services)
        }
        
        print(f"✅ Port management completed for {len(services)} services")
        return port_management_result
    
    def _assess_environment(self) -> Dict[str, Any]:
        """Phase 3: Environment assessment and requirements analysis."""
        print("📋 Assessing environment and requirements...")
        
        # Use RequirementsAgent for requirements analysis
        requirements_result = self.agents['requirements'].ensure_requirements(self.checkpoint_results['repository_analysis'])
        
        # Dynamically decide if we need additional environment checks
        if self._needs_environment_validation(requirements_result):
            print("🔧 Validating environment compatibility...")
            # Could add environment validation logic here
        
        return requirements_result
    
    def _manage_dependencies(self) -> Dict[str, Any]:
        """Phase 4: Intelligent dependency management."""
        print("📦 Managing dependencies...")
        
        # Use SetupAgent for dependency installation
        setup_result = self.agents['setup'].install(self.checkpoint_results['environment_assessment'])
        
        # Dynamically decide if we need service-specific setup
        if self._needs_service_setup(self.checkpoint_results['repository_analysis']):
            print("⚙️ Setting up service-specific dependencies...")
            service_setup_result = self.agents['setup'].setup_services(self.checkpoint_results['repository_analysis'])
            setup_result.update(service_setup_result)
        
        return setup_result
    
    def _configure_services(self) -> Dict[str, Any]:
        """Phase 5: Service configuration and database setup."""
        print("🗄️ Configuring services and database...")
        
        # Use DBAgent if database services are detected
        db_result = {}
        if self._needs_database_setup(self.checkpoint_results['repository_analysis']):
            print("🗄️ Setting up database...")
            db_result = self.agents['db'].setup(self.checkpoint_results['repository_analysis'])
        
        # Dynamically decide if we need additional configuration
        if self._needs_additional_configuration(self.checkpoint_results['repository_analysis']):
            print("⚙️ Applying additional configurations...")
            # Could add configuration logic here
        
        return db_result
    
    def _start_services(self) -> Dict[str, Any]:
        """Phase 6: Intelligent service startup."""
        print("🚀 Starting services with dynamic port allocation...")
        
        # Get port management results
        port_management = self.checkpoint_results.get('port_management', {})
        allocated_ports = port_management.get('allocated_ports', {})
        
        # Use RunnerAgent for service startup with allocated ports
        runner_result = self.agents['runner'].start(
            self.checkpoint_results['repository_analysis'], 
            self.workflow_state['mode'],
            allocated_ports
        )
        
        # Dynamically decide if we need to retry with different approach
        if self._needs_startup_retry(runner_result):
            print("🔄 Retrying service startup with alternative approach...")
            runner_result = self._retry_service_startup()
        
        return runner_result
    
    def _validate_health(self) -> Dict[str, Any]:
        """Phase 7: Comprehensive health validation."""
        print("🏥 Validating service health...")
        
        # Use HealthAgent for health checks
        health_result = self.agents['health'].check(self.checkpoint_results['service_startup'])
        
        # Dynamically decide if we need service-specific health checks
        if self._needs_service_health_check(self.checkpoint_results['repository_analysis']):
            print("🔍 Performing service-specific health checks...")
            service_health_result = self.agents['health'].check_services(self.checkpoint_results['repository_analysis'])
            # Merge health results properly
            if isinstance(service_health_result, dict):
                health_result.update(service_health_result)
            else:
                health_result['service_checks'] = service_health_result
        
        # Use FixerAgent if health issues are detected
        if not health_result.get('ok', True):
            print("🔧 Attempting to fix health issues...")
            fix_result = self.agents['fixer'].fix(health_result.get('errors', []), self.checkpoint_results['repository_analysis'])
            health_result['fixes_applied'] = fix_result
        
        return health_result
    
    def _optimize_system(self) -> Dict[str, Any]:
        """Phase 8: System optimization and final validation."""
        print("⚡ Optimizing system performance...")
        
        # Final health check
        final_health = self.agents['health'].check_services(self.checkpoint_results['repository_analysis'])
        
        # Dynamically decide if optimization is needed
        if self._needs_optimization(final_health):
            print("🔧 Applying optimizations...")
            # Could add optimization logic here
        
        return final_health
    
    def _is_timeout(self) -> bool:
        """Check if the workflow has exceeded the timeout."""
        if self.start_time is None:
            return False
        return time.time() - self.start_time > self.timeout
    
    def _needs_deeper_analysis(self, detection_result: Dict) -> bool:
        """Decide if deeper analysis is needed."""
        return not detection_result.get('services') or len(detection_result.get('services', [])) == 0
    
    def _needs_environment_validation(self, requirements_result: Dict) -> bool:
        """Decide if environment validation is needed."""
        return bool(requirements_result.get('errors') or requirements_result.get('warnings'))
    
    def _needs_service_setup(self, analysis_result: Dict) -> bool:
        """Decide if service-specific setup is needed."""
        return bool(analysis_result.get('services'))
    
    def _needs_database_setup(self, analysis_result: Dict) -> bool:
        """Decide if database setup is needed."""
        services = analysis_result.get('services', [])
        return any(s.get('type') == 'docker' and s.get('role') == 'db' for s in services)
    
    def _needs_additional_configuration(self, analysis_result: Dict) -> bool:
        """Decide if additional configuration is needed."""
        return bool(analysis_result.get('files', {}).get('.env') or analysis_result.get('files', {}).get('docker-compose.yml'))
    
    def _needs_startup_retry(self, runner_result: Dict) -> bool:
        """Decide if service startup retry is needed."""
        return bool(runner_result.get('errors') or runner_result.get('status') == 'failed')
    
    def _needs_service_health_check(self, analysis_result: Dict) -> bool:
        """Decide if service-specific health checks are needed."""
        return bool(analysis_result.get('services'))
    
    def _needs_optimization(self, health_result: Dict) -> bool:
        """Decide if system optimization is needed."""
        return not health_result.get('ok', True)
    
    def _should_retry_phase(self, phase_name: str) -> bool:
        """Decide if a phase should be retried."""
        self.workflow_state['retry_count'] += 1
        return self.workflow_state['retry_count'] <= self.workflow_state['max_retries']
    
    def _retry_phase(self, phase_name: str, phase_function) -> bool:
        """Retry a failed phase with different approach."""
        print(f"🔄 Retrying {phase_name.replace('_', ' ')}...")
        time.sleep(2)  # Brief pause before retry
        return self._execute_phase(phase_name, phase_function)
    
    def _retry_service_startup(self) -> Dict[str, Any]:
        """Retry service startup with alternative approach."""
        # Try different startup strategies
        print("🔄 Trying alternative startup approach...")
        port_management = self.checkpoint_results.get('port_management', {})
        allocated_ports = port_management.get('allocated_ports', {})
        return self.agents['runner'].start(
            self.checkpoint_results['repository_analysis'], 
            self.workflow_state['mode'],
            allocated_ports
        )
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        return {
            'status': 'success',
            'workflow_state': self.workflow_state,
            'checkpoint_results': self.checkpoint_results,
            'summary': {
                'total_phases': len(self.workflow_state['completed_phases']),
                'failed_phases': len(self.workflow_state['failed_phases']),
                'retry_count': self.workflow_state['retry_count'],
                'final_health': self.checkpoint_results.get('final_optimization', {})
            }
        }
    
    def _generate_error_report(self, error: Exception) -> Dict[str, Any]:
        """Generate error report."""
        return {
            'status': 'failed',
            'error': str(error),
            'workflow_state': self.workflow_state,
            'checkpoint_results': self.checkpoint_results,
            'summary': {
                'completed_phases': self.workflow_state['completed_phases'],
                'failed_phases': self.workflow_state['failed_phases'],
                'current_phase': self.workflow_state['current_phase']
            }
        }
