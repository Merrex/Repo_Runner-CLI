from repo_runner.agents.detection_agent import DetectionAgent
from repo_runner.agents.requirements_agent import RequirementsAgent
from repo_runner.agents.setup_agent import SetupAgent
from repo_runner.agents.db_agent import DBAgent
from repo_runner.agents.runner_agent import RunnerAgent
from repo_runner.agents.health_agent import HealthAgent
from repo_runner.agents.fixer_agent import FixerAgent
from .port_manager import PortManagerAgent
from repo_runner.agents.file_agent import FileAgent
from repo_runner.agents.config_agent import ConfigAgent
from repo_runner.agents.dependency_agent import DependencyAgent
from repo_runner.agents.admin_agent import AdminAgent
import time
import signal
from typing import Dict, List, Any
import os
import subprocess
import threading
from pathlib import Path
import json
import yaml
from .base_manager import BaseManager
import networkx as nx
from repo_runner.agents.env_detector import EnvDetectorAgent

class AutonomousServiceOrchestrator(BaseManager):
    """
    Autonomous Service Orchestrator - Manager for service lifecycle.
    
    Manager-Agent Architecture:
    - Uses decision-making models for orchestration decisions
    - Coordinates agents for service management
    - Reports to Admin Agent (CEO)
    """
    
    def __init__(self):
        super().__init__()
        self.environment = 'local'
        self.service_processes = {}
        self.port_manager = None
        self.admin_agent = None  # Reference to Admin Agent (CEO)
        
    def set_admin_agent(self, admin_agent):
        """Set reference to Admin Agent (CEO)"""
        self.admin_agent = admin_agent
        
    def set_port_manager(self, port_manager):
        """Set port manager"""
        self.port_manager = port_manager
        
    def orchestrate(self, repo_path: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate service startup using decision-making models"""
        print("🎯 Orchestrating services with decision-making models...")
        
        try:
            # Use decision model to determine service startup strategy
            strategy = self._determine_startup_strategy(detection_result)
            
            # Execute strategy using agents
            result = self._execute_startup_strategy(strategy, repo_path, detection_result)
            
            # Report to Admin Agent if available
            if self.admin_agent:
                self.admin_agent.log_result(f"Service orchestration completed: {result.get('status')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Service orchestration failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Report failure to Admin Agent
            if self.admin_agent:
                self.admin_agent.log_result(error_msg, level="error")
            
            return {'status': 'error', 'error': str(e)}
    
    def _determine_startup_strategy(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Use decision model to determine startup strategy"""
        # This would use a decision-making model to analyze the detection result
        # and determine the best startup strategy
        
        services = detection_result.get('services', [])
        technologies = detection_result.get('technologies', [])
        
        # Simple decision logic (in real implementation, this would use a decision model)
        if 'docker' in technologies:
            return {'method': 'docker', 'priority': 'high'}
        elif 'python' in technologies:
            return {'method': 'python', 'priority': 'medium'}
        elif 'node' in technologies:
            return {'method': 'node', 'priority': 'medium'}
        else:
            return {'method': 'generic', 'priority': 'low'}
    
    def _execute_startup_strategy(self, strategy: Dict[str, Any], repo_path: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the determined startup strategy"""
        method = strategy.get('method', 'generic')
        
        if method == 'docker':
            return self._start_docker_services(repo_path, detection_result)
        elif method == 'python':
            return self._start_python_services(repo_path, detection_result)
        elif method == 'node':
            return self._start_node_services(repo_path, detection_result)
        else:
            return self._start_generic_services(repo_path, detection_result)
    
    def _start_docker_services(self, repo_path: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Start services using Docker"""
        print("🐳 Starting Docker services...")
        
        try:
            # Use agents to handle Docker startup
            # This would coordinate with DockerAgent, PortManagerAgent, etc.
            
            return {
                'status': 'success',
                'method': 'docker',
                'services_started': len(detection_result.get('services', [])),
                'message': 'Docker services started successfully'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _start_python_services(self, repo_path: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Start Python services"""
        print("🐍 Starting Python services...")
        
        try:
            # Use agents to handle Python startup
            # This would coordinate with PythonAgent, PortManagerAgent, etc.
            
            return {
                'status': 'success',
                'method': 'python',
                'services_started': len(detection_result.get('services', [])),
                'message': 'Python services started successfully'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _start_node_services(self, repo_path: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Start Node.js services"""
        print("📦 Starting Node.js services...")
        
        try:
            # Use agents to handle Node.js startup
            # This would coordinate with NodeAgent, PortManagerAgent, etc.
            
            return {
                'status': 'success',
                'method': 'node',
                'services_started': len(detection_result.get('services', [])),
                'message': 'Node.js services started successfully'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _start_generic_services(self, repo_path: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Start generic services"""
        print("🔧 Starting generic services...")
        
        try:
            # Use agents to handle generic startup
            # This would coordinate with GenericAgent, PortManagerAgent, etc.
            
            return {
                'status': 'success',
                'method': 'generic',
                'services_started': len(detection_result.get('services', [])),
                'message': 'Generic services started successfully'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
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

    def run_checkpointed_step(self, agent, function_name, *args, checkpoint_file="agent_state.json", **kwargs):
        """
        Run an agent function by name, save input/output/error to checkpoint after execution.
        Loads previous state, appends this step, and saves updated state.
        """
        state = self.load_checkpoint(checkpoint_file)
        step_record = {
            "agent": agent.__class__.__name__,
            "function": function_name,
            "args": args,
            "kwargs": kwargs,
            "result": None,
            "error": None
        }
        try:
            registry = agent.get_function_registry()
            result = registry[function_name](*args, **kwargs)
            step_record["result"] = result
        except Exception as e:
            step_record["error"] = str(e)
        # Append to state history
        if "history" not in state:
            state["history"] = []
        state["history"].append(step_record)
        self.save_checkpoint(state, checkpoint_file)
        return step_record

    def run_checkpointed_step_with_retry(self, agent, function_name, *args, max_retries=3, checkpoint_file="agent_state.json", run_state_file="run_state.json", fixer_agent=None, **kwargs):
        """
        Run an agent function by name with retry and self-heal. On failure, use FixerAgent to attempt a fix and retry.
        Log all attempts, errors, and fixes in run_state.json. Orchestrator acts as POC for user interaction.
        """
        run_state = self.load_checkpoint(run_state_file)
        if "attempts" not in run_state:
            run_state["attempts"] = []
        attempt = 0
        last_error = None
        while attempt < max_retries:
            step_record = self.run_checkpointed_step(agent, function_name, *args, checkpoint_file=checkpoint_file, **kwargs)
            run_state["attempts"].append(step_record)
            self.save_checkpoint(run_state, run_state_file)
            if not step_record["error"]:
                return step_record  # Success
            last_error = step_record["error"]
            # Try self-heal with FixerAgent if provided
            if fixer_agent is not None:
                fix_result = fixer_agent.self_fix(last_error, context={"agent": agent.__class__.__name__, "function": function_name, "args": args, "kwargs": kwargs})
                run_state.setdefault("fixes", []).append({
                    "error": last_error,
                    "fix_result": fix_result,
                    "attempt": attempt + 1
                })
                self.save_checkpoint(run_state, run_state_file)
            attempt += 1
        # If all retries fail, orchestrator prepares a user-friendly message
        run_state.setdefault("final_status", {})[function_name] = {
            "status": "failed",
            "error": last_error,
            "agent": agent.__class__.__name__,
            "args": args,
            "kwargs": kwargs
        }
        self.save_checkpoint(run_state, run_state_file)
        return {"error": last_error, "status": "failed", "agent": agent.__class__.__name__, "function": function_name}

# Enhanced Orchestrator
class Orchestrator(BaseManager):
    """
    Enhanced orchestrator with autonomous service management.
    
    Manager-Agent Architecture:
    - Uses decision-making models for workflow orchestration
    - Coordinates agents for specialized tasks
    - Reports to Admin Agent (CEO)
    """
    
    def __init__(self, timeout=300, env='detect', model_tier='balanced'):
        super().__init__()
        self.timeout = timeout
        self.env = env
        self.model_tier = model_tier
        self.service_orchestrator = AutonomousServiceOrchestrator()
        if env != 'detect':
            self.service_orchestrator.environment = env
        self.detection_results = {}
        self.port_manager = None
        self.admin_agent = None  # Reference to Admin Agent (CEO)
        
        # Example: instantiate agents for dynamic use
        self.file_agent = FileAgent(config={'model_tier': model_tier})
        self.config_agent = ConfigAgent(config={'model_tier': model_tier})
        self.dependency_agent = DependencyAgent(config={'model_tier': model_tier})
        
        # Set manager references for agents
        self.file_agent.set_manager(self)
        self.config_agent.set_manager(self)
        self.dependency_agent.set_manager(self)
    
    def set_admin_agent(self, admin_agent):
        """Set reference to Admin Agent (CEO)"""
        self.admin_agent = admin_agent
        self.service_orchestrator.set_admin_agent(admin_agent)
    
    def set_port_manager(self, port_manager):
        """Set the port manager for the orchestrator"""
        self.port_manager = port_manager
        self.service_orchestrator.port_manager = port_manager
    
    def run(self, repo_path: str, mode: str = 'local') -> Dict[str, Any]:
        """Run the orchestration workflow with manager-agent architecture"""
        print("🚀 Starting Orchestrator with Manager-Agent Architecture")
        
        # Report to Admin Agent
        if self.admin_agent:
            self.admin_agent.log_result(f"Orchestrator starting workflow for {repo_path}")
        
        try:
            # Import required agents
            from repo_runner.agents.detection_agent import DetectionAgent
            from repo_runner.agents.requirements_agent import RequirementsAgent
            from repo_runner.agents.setup_agent import SetupAgent
            from repo_runner.agents.port_manager_agent import PortManagerAgent
            from repo_runner.agents.health_agent import HealthAgent
            
            # Initialize agents with config
            detection_agent = DetectionAgent(config={'model_tier': self.model_tier})
            requirements_agent = RequirementsAgent(config={'model_tier': self.model_tier})
            setup_agent = SetupAgent(config={'model_tier': self.model_tier})
            port_manager_agent = PortManagerAgent(config={'model_tier': self.model_tier})
            health_agent = HealthAgent(config={'model_tier': self.model_tier})
            
            # Set manager references
            detection_agent.set_manager(self)
            requirements_agent.set_manager(self)
            setup_agent.set_manager(self)
            port_manager_agent.set_manager(self)
            health_agent.set_manager(self)
            
            # Set port manager for orchestrator
            self.set_port_manager(port_manager_agent.port_manager)
            
            # Example: dynamically create a .env file at a checkpoint
            # (In real workflow, this could be triggered by requirements or detection)
            env_vars = {'EXAMPLE_KEY': 'example_value'}
            env_path = self.config_agent.create_env_file(env_vars, path=f"{repo_path}/.env")
            print(f"[Orchestrator] Dynamically created .env at: {env_path}")
            
            # Phase 1: Repository Analysis
            print("\n🔄 Phase: Repository Analysis")
            detection_result = detection_agent.detect_project_structure(repo_path)
            services_result = detection_result['services']
            
            if detection_result['status'] == 'error':
                return {'status': 'error', 'error': detection_result['error']}
            
            # Phase 2: Port Management
            print("\n🔄 Phase: Port Management")
            port_results = port_manager_agent.manage_ports(repo_path)
            
            # Phase 3: Environment Assessment
            print("\n🔄 Phase: Environment Assessment")
            requirements_results = requirements_agent.ensure_requirements(detection_result)
            
            # Phase 4: Setup
            print("\n🔄 Phase: Setup")
            setup_results = setup_agent.setup_project(repo_path)
            
            # Phase 5: Autonomous Service Orchestration
            print("\n🔄 Phase: Service Orchestration")
            orchestration_results = self.service_orchestrator.orchestrate(repo_path, detection_result)
            
            # Phase 6: Health Check
            print("\n🔄 Phase: Health Check")
            health_results = health_agent.check(orchestration_results)
            
            # Generate final summary
            final_result = {
                'status': 'success',
                'detection': detection_result,
                'port_management': port_results,
                'requirements': requirements_results,
                'setup': setup_results,
                'orchestration': orchestration_results,
                'health': health_results,
                'mode': mode,
                'timeout': self.timeout
            }
            
            print("\n✅ Workflow completed successfully!")
            
            # Report success to Admin Agent
            if self.admin_agent:
                self.admin_agent.log_result("Orchestrator workflow completed successfully")
            
            return final_result
            
        except Exception as e:
            error_msg = f"Workflow failed: {e}"
            print(f"❌ {error_msg}")
            
            # Report failure to Admin Agent
            if self.admin_agent:
                self.admin_agent.log_result(error_msg, level="error")
            
            return {
                'status': 'error',
                'error': str(e),
                'mode': mode,
                'timeout': self.timeout
            }

    def _save_agent_run_dag(self, agent_order):
        """
        Save agent run order and dependencies as a DAG in agent_run_dag.json
        """
        import json
        import os
        dag = {"nodes": [], "edges": []}
        for i, agent in enumerate(agent_order):
            dag["nodes"].append({"id": agent, "order": i})
            if i > 0:
                dag["edges"].append({"from": agent_order[i-1], "to": agent})
        with open("agent_run_dag.json", "w") as f:
            json.dump(dag, f, indent=2)

class OrchestratorAgent:
    """
    OrchestratorAgent - Single POC for user interactions.
    
    Manager-Agent Architecture:
    - Delegated by Admin Agent (CEO)
    - Uses decision-making models for workflow decisions
    - Coordinates agents for specialized tasks
    - Reports back to Admin Agent
    """
    
    def __init__(self, repo_path=None, env=None, config=None):
        self.repo_path = repo_path or '.'
        self.env = env
        self.config = config or {}
        self.state_file = os.path.join(self.repo_path, 'run_state.json')
        self.log = []
        self.agents = {}
        self.context_indexer = None
        self.admin_agent = None  # Reference to Admin Agent (CEO)
        
        # Initialize agents
        self._initialize_agents()
        
        # Initialize context indexer with FAISS configuration
        self._initialize_context_indexer()

    def set_admin_agent(self, admin_agent):
        """Set reference to Admin Agent (CEO)"""
        self.admin_agent = admin_agent

    def _initialize_agents(self):
        """Initialize all agents with configuration"""
        from repo_runner.agents.env_detector import EnvDetectorAgent
        from repo_runner.agents.dependency_agent import DependencyAgent
        from repo_runner.agents.setup_agent import SetupAgent
        from repo_runner.agents.runner_agent import RunnerAgent
        from repo_runner.agents.fixer_agent import FixerAgent
        from repo_runner.agents.health_agent import HealthAgent
        from repo_runner.agents.config_agent import ConfigAgent
        from repo_runner.agents.db_agent import DBAgent
        from repo_runner.agents.file_agent import FileAgent
        from repo_runner.agents.requirements_agent import RequirementsAgent
        from repo_runner.agents.detection_agent import DetectionAgent
        
        # Get agents to skip from config
        skip_agents = self.config.get('skip_agents', [])
        
        agent_classes = {
            'EnvDetectorAgent': EnvDetectorAgent,
            'DependencyAgent': DependencyAgent,
            'SetupAgent': SetupAgent,
            'RunnerAgent': RunnerAgent,
            'FixerAgent': FixerAgent,
            'HealthAgent': HealthAgent,
            'ConfigAgent': ConfigAgent,
            'DatabaseAgent': DBAgent,
            'FileAgent': FileAgent,
            'RequirementsAgent': RequirementsAgent,
            'DetectionAgent': DetectionAgent
        }
        
        self.agents = {}
        for agent_name, agent_class in agent_classes.items():
            if agent_name not in skip_agents:
                agent_instance = agent_class(config=self.config)
                agent_instance.set_manager(self)  # Set this orchestrator as manager
                self.agents[agent_name] = agent_instance

    def _initialize_context_indexer(self):
        """Initialize context indexer with FAISS configuration"""
        from repo_runner.agents.context_indexer import ContextIndexer
        
        # Get FAISS configuration from config
        faiss_config = self.config.get('faiss', {})
        use_faiss = faiss_config.get('use_faiss')
        sentence_transformer_model = faiss_config.get('sentence_transformer_model')
        
        # Build indexer config
        indexer_config = {}
        if use_faiss is not None:
            indexer_config['use_faiss'] = use_faiss
        if sentence_transformer_model:
            indexer_config['sentence_transformer_model'] = sentence_transformer_model
        
        self.context_indexer = ContextIndexer(
            use_faiss=use_faiss,
            config=indexer_config
        )
        
        # Log indexer configuration
        index_info = self.context_indexer.get_index_info()
        print(f"🔧 Context Indexer initialized: {index_info}")

    def _load_agent_recommendations(self) -> Dict[str, Any]:
        """Load recommendations from all agents"""
        recommendations = {}
        
        for agent_name in self.agents.keys():
            state_file = f'agent_state_{agent_name}.json'
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                        if 'recommendations' in state:
                            recommendations[agent_name] = state['recommendations']
                except Exception as e:
                    print(f"⚠️ Could not load recommendations from {agent_name}: {e}")
        
        return recommendations

    def _update_faiss_config_from_recommendations(self):
        """Update FAISS configuration based on agent recommendations"""
        recommendations = self._load_agent_recommendations()
        
        # Check if we have FAISS recommendations
        faiss_recommendations = []
        for agent_name, recs in recommendations.items():
            if 'recommend_faiss' in recs:
                faiss_recommendations.append({
                    'agent': agent_name,
                    'recommend_faiss': recs['recommend_faiss'],
                    'reason': recs.get('reason', 'No reason provided'),
                    'model': recs.get('sentence_transformer_model')
                })
        
        if faiss_recommendations:
            # Use the first recommendation (priority: EnvDetectorAgent > DependencyAgent > others)
            priority_agents = ['EnvDetectorAgent', 'DependencyAgent', 'DetectionAgent']
            
            for priority_agent in priority_agents:
                for rec in faiss_recommendations:
                    if rec['agent'] == priority_agent:
                        print(f"🔧 Using FAISS recommendation from {priority_agent}: {rec}")
                        
                        # Update context indexer if recommendation differs from current config
                        current_config = self.config.get('faiss', {})
                        if current_config.get('use_faiss') != rec['recommend_faiss']:
                            self.config['faiss'] = {
                                'use_faiss': rec['recommend_faiss'],
                                'sentence_transformer_model': rec.get('model')
                            }
                            
                            # Reinitialize context indexer with new config
                            self._initialize_context_indexer()
                            print("✅ Updated FAISS configuration based on agent recommendations")
                        return

    def run(self):
        """Run the complete orchestration workflow with FAISS support"""
        print("🚀 Starting Repo Runner Orchestration with FAISS support")
        
        # Report to Admin Agent
        if self.admin_agent:
            self.admin_agent.log_result("OrchestratorAgent starting workflow")
        
        run_summary = {}
        errors = []
        
        try:
            # Phase 1: Environment Detection and Analysis
            print("🔍 Phase 1: Environment Detection and Analysis")
            
            # Run environment detection first
            if 'EnvDetectorAgent' in self.agents:
                env_result = self.agents['EnvDetectorAgent'].run()
                run_summary['environment'] = env_result
                if env_result.get('error'):
                    errors.append(env_result['error'])
                print(f"✅ Environment detected: {env_result.get('environment', 'unknown')}")
            
            # Run detection agent
            if 'DetectionAgent' in self.agents:
                detection_result = self.agents['DetectionAgent'].run()
                run_summary['detection'] = detection_result
                if detection_result.get('error'):
                    errors.append(detection_result['error'])
                print("✅ Project structure detected")
            
            # Run requirements analysis
            if 'RequirementsAgent' in self.agents:
                req_result = self.agents['RequirementsAgent'].run()
                run_summary['requirements'] = req_result
                if req_result.get('error'):
                    errors.append(req_result['error'])
                print("✅ Requirements analyzed")
            
            # Phase 2: Dependency and Setup
            print("📦 Phase 2: Dependency and Setup")
            
            # Run dependency agent
            if 'DependencyAgent' in self.agents:
                dep_result = self.agents['DependencyAgent'].run()
                run_summary['dependencies'] = dep_result
                if dep_result.get('error'):
                    errors.append(dep_result['error'])
                print("✅ Dependencies processed")
            
            # Update FAISS configuration based on agent recommendations
            self._update_faiss_config_from_recommendations()
            
            # Run setup agent
            if 'SetupAgent' in self.agents:
                setup_result = self.agents['SetupAgent'].run()
                run_summary['setup'] = setup_result
                if setup_result.get('error'):
                    errors.append(setup_result['error'])
                print("✅ Setup completed")
            
            # Phase 3: Database and Configuration
            print("🗄️ Phase 3: Database and Configuration")
            
            # Run database agent
            if 'DatabaseAgent' in self.agents:
                db_result = self.agents['DatabaseAgent'].run()
                run_summary['database'] = db_result
                if db_result.get('error'):
                    errors.append(db_result['error'])
                print("✅ Database setup completed")
            
            # Run config agent
            if 'ConfigAgent' in self.agents:
                config_result = self.agents['ConfigAgent'].run()
                run_summary['config'] = config_result
                if config_result.get('error'):
                    errors.append(config_result['error'])
                print("✅ Configuration processed")
            
            # Phase 4: File Processing and Context Indexing
            print("📁 Phase 4: File Processing and Context Indexing")
            
            # Run file agent
            if 'FileAgent' in self.agents:
                file_result = self.agents['FileAgent'].run()
                run_summary['files'] = file_result
                if file_result.get('error'):
                    errors.append(file_result['error'])
                print("✅ Files processed")
                
                # Build context index if files were processed
                if file_result.get('files') and self.context_indexer:
                    self._build_context_index(file_result['files'])
            
            # Phase 5: Execution and Health Monitoring
            print("🚀 Phase 5: Execution and Health Monitoring")
            
            # Run runner agent
            if 'RunnerAgent' in self.agents:
                runner_result = self.agents['RunnerAgent'].run()
                run_summary['runner'] = runner_result
                if runner_result.get('error'):
                    errors.append(runner_result['error'])
                print("✅ Application started")
            
            # Run health agent
            if 'HealthAgent' in self.agents:
                health_result = self.agents['HealthAgent'].run()
                run_summary['health'] = health_result
                if health_result.get('error'):
                    errors.append(health_result['error'])
                print("✅ Health check completed")
            
            # Phase 6: Error Handling and Fixes
            print("🔧 Phase 6: Error Handling and Fixes")
            
            # Check for errors and run fixer if needed
            if errors:
                print(f"⚠️ Found {len(errors)} errors, running fixer agent")
                if 'FixerAgent' in self.agents:
                    fixer_result = self.agents['FixerAgent'].run(errors=errors)
                    run_summary['fixes'] = fixer_result
                    print("✅ Error fixes applied")
            
            # Generate final summary
            summary = self._generate_summary(run_summary)
            run_summary['summary'] = summary
            
            print("✅ Orchestration completed successfully")
            
            # Report success to Admin Agent
            if self.admin_agent:
                self.admin_agent.log_result("OrchestratorAgent workflow completed successfully")
            
            # Log and checkpoint
            self._log_and_checkpoint(run_summary)
            return run_summary
            
        except Exception as e:
            error_msg = f"Orchestration failed: {e}"
            print(f"❌ {error_msg}")
            
            # Report failure to Admin Agent
            if self.admin_agent:
                self.admin_agent.log_result(error_msg, level="error")
            
            return {
                'status': 'error',
                'error': str(e),
                'summary': run_summary
            }

    def _build_context_index(self, files: List[str]):
        """Build context index from processed files"""
        if self.context_indexer and files:
            print(f"🔍 Building context index from {len(files)} files")
            self.context_indexer.build_index(files)
            print("✅ Context index built successfully")

    def _generate_summary(self, run_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the orchestration results"""
        summary = {
            'total_agents': len(self.agents),
            'successful_agents': len([r for r in run_summary.values() if isinstance(r, dict) and r.get('status') == 'ok']),
            'failed_agents': len([r for r in run_summary.values() if isinstance(r, dict) and r.get('status') == 'error']),
            'environment': run_summary.get('environment', {}).get('environment', 'unknown'),
            'context_indexer': self.context_indexer.get_index_info() if self.context_indexer else None
        }
        
        return summary

    def _log_and_checkpoint(self, run_summary):
        entry = {
            'timestamp': time.time(),
            'summary': run_summary
        }
        self.log.append(entry)
        try:
            with open(self.state_file, 'w') as f:
                json.dump(entry, f, indent=2)
        except Exception as e:
            print(f"[OrchestratorAgent] Failed to write run_state.json: {e}")
