from .detection_agent import DetectionAgent
from .requirements_agent import RequirementsAgent
from .setup_agent import SetupAgent
from .db_agent import DBAgent
from .runner_agent import RunnerAgent
from .health_agent import HealthAgent
from .fixer_agent import FixerAgent
from .port_manager_agent import PortManagerAgent

class Orchestrator:
    def run(self, repo_path, mode="local"):
        # Initialize agents
        detection_agent = DetectionAgent()
        requirements_agent = RequirementsAgent()
        setup_agent = SetupAgent()
        db_agent = DBAgent()
        runner_agent = RunnerAgent()
        health_agent = HealthAgent()
        fixer_agent = FixerAgent()
        port_manager = PortManagerAgent()
        
        # Step 1: Detect repository structure and services
        print("🔍 Analyzing repository structure...")
        structure = detection_agent.analyze(repo_path)
        
        # Step 2: Detect services and manage ports
        print("🔌 Managing port allocation...")
        services = detection_agent.detect_services(repo_path)
        port_config = port_manager.get_port_configuration(services.get('services', []))
        
        # Add port configuration to structure
        structure['port_config'] = port_config
        structure['services'] = services.get('services', [])
        
        # Step 3: Ensure requirements
        print("📦 Checking requirements...")
        reqs = requirements_agent.ensure_requirements(structure)
        
        # Step 4: Setup environment and install dependencies
        print("⚙️ Setting up environment...")
        setup_agent.install(reqs)
        setup_agent.setup_services(structure)
        
        # Step 5: Setup database if needed
        print("🗄️ Setting up database...")
        db_status = db_agent.setup(structure)
        
        # Step 6: Start services with proper port allocation
        print("🚀 Starting services...")
        run_status = runner_agent.start(structure, mode)
        
        # Step 7: Check health of running services
        print("🏥 Checking service health...")
        health = health_agent.check(run_status)
        
        # Step 8: Fix issues if any
        if not health.get("ok"):
            print("🔧 Fixing issues...")
            fix = fixer_agent.fix(health.get("errors", []), structure)
            # Optionally, retry setup/run after fix
        
        # Step 9: Final health check with port validation
        print("✅ Final validation...")
        final_health = health_agent.check_services(structure)
        
        return {
            'health': health,
            'port_config': port_config,
            'services': structure.get('services', []),
            'final_health': final_health
        } 