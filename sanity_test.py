#!/usr/bin/env python3
"""
Sanity Test for Repo Runner

Quick test to verify basic functionality works.
"""

import os
import sys
import tempfile
import shutil

# Add the project to Python path
project_path = os.path.join(os.getcwd(), 'project')
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, 'repo_runner'))

def create_simple_test_repo():
    """Create a simple test repository."""
    test_repo_path = tempfile.mkdtemp(prefix="sanity_test_")
    
    # Simple Flask app
    app_code = '''from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, Sanity Test!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
'''
    
    requirements = '''flask==2.3.3
'''
    
    readme = '''# Sanity Test App
Simple Flask application for testing.
'''
    
    with open(os.path.join(test_repo_path, "app.py"), "w") as f:
        f.write(app_code)
    
    with open(os.path.join(test_repo_path, "requirements.txt"), "w") as f:
        f.write(requirements)
    
    with open(os.path.join(test_repo_path, "README.md"), "w") as f:
        f.write(readme)
    
    return test_repo_path

def run_sanity_test():
    """Run a quick sanity test."""
    print("🧪 Running Sanity Test")
    print("=" * 30)
    
    test_repo_path = create_simple_test_repo()
    print(f"✅ Created test repo: {test_repo_path}")
    
    try:
        # Test 1: Import agents
        print("\n1. Testing agent imports...")
        from repo_runner.agents.detection_agent import DetectionAgent
        from repo_runner.agents.requirements_agent import RequirementsAgent
        from repo_runner.agents.setup_agent import SetupAgent
        from repo_runner.agents.port_manager_agent import PortManagerAgent
        from repo_runner.agents.orchestrator import Orchestrator
        print("✅ All agents imported successfully")
        
        # Test 2: Detection
        print("\n2. Testing detection...")
        detection_agent = DetectionAgent()
        repo_analysis = detection_agent.analyze(test_repo_path)
        services = detection_agent.detect_services(test_repo_path)
        print(f"✅ Detection completed: {len(services.get('services', []))} services found")
        
        # Test 3: Requirements
        print("\n3. Testing requirements analysis...")
        requirements_agent = RequirementsAgent()
        requirements_result = requirements_agent.ensure_requirements(repo_analysis)
        print(f"✅ Requirements analyzed: {requirements_result.get('status')}")
        
        # Test 4: Port Management
        print("\n4. Testing port management...")
        port_manager = PortManagerAgent()
        allocated_ports = port_manager.allocate_ports_for_services(services.get('services', []))
        print(f"✅ Ports allocated: {allocated_ports}")
        
        # Test 5: Setup
        print("\n5. Testing setup...")
        setup_agent = SetupAgent()
        setup_result = setup_agent.install(requirements_result)
        print(f"✅ Setup completed: {setup_result.get('status', 'unknown')}")
        
        # Test 6: Orchestrator
        print("\n6. Testing orchestrator...")
        orchestrator = Orchestrator(timeout=120)
        final_result = orchestrator.run(test_repo_path, "local")
        print(f"✅ Orchestrator completed: {final_result.get('status')}")
        
        print("\n🎉 Sanity test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Sanity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(test_repo_path)
            print(f"🧹 Cleaned up: {test_repo_path}")
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")

if __name__ == "__main__":
    success = run_sanity_test()
    sys.exit(0 if success else 1) 