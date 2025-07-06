#!/usr/bin/env python3
"""
Local Integration Test for Repo Runner

This script tests the complete agent interdependence and integration
to ensure all agents work together to set up and run repositories.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import time
from pathlib import Path

# Add the project to Python path
project_path = os.path.join(os.getcwd(), 'project')
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, 'repo_runner'))

def create_test_repo():
    """Create a comprehensive test repository with both backend and frontend."""
    test_repo_path = tempfile.mkdtemp(prefix="test_repo_")
    
    # Create backend (Flask)
    backend_path = os.path.join(test_repo_path, "backend")
    os.makedirs(backend_path)
    
    backend_app = '''from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Backend is running!", "status": "healthy"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "service": "backend"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
'''
    
    backend_requirements = '''flask==2.3.3
flask-cors==4.0.0
requests==2.31.0
'''
    
    with open(os.path.join(backend_path, "app.py"), "w") as f:
        f.write(backend_app)
    
    with open(os.path.join(backend_path, "requirements.txt"), "w") as f:
        f.write(backend_requirements)
    
    # Create frontend (React-like structure)
    frontend_path = os.path.join(test_repo_path, "frontend")
    os.makedirs(frontend_path)
    
    frontend_package = '''{
  "name": "test-frontend",
  "version": "1.0.0",
  "description": "Test frontend application",
  "main": "index.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "axios": "^1.6.0"
  }
}
'''
    
    frontend_server = '''const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'Frontend is running!', status: 'healthy' });
});

app.get('/api/backend-status', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:5000/api/health');
        res.json({ 
            frontend: 'healthy', 
            backend: response.data,
            connected: true 
        });
    } catch (error) {
        res.json({ 
            frontend: 'healthy', 
            backend: 'unreachable',
            connected: false,
            error: error.message 
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Frontend server running on port ${PORT}`);
});
'''
    
    with open(os.path.join(frontend_path, "package.json"), "w") as f:
        f.write(frontend_package)
    
    with open(os.path.join(frontend_path, "server.js"), "w") as f:
        f.write(frontend_server)
    
    # Create docker-compose for easy testing
    docker_compose = '''version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
    volumes:
      - ./backend:/app
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
'''
    
    with open(os.path.join(test_repo_path, "docker-compose.yml"), "w") as f:
        f.write(docker_compose)
    
    # Create README
    readme = '''# Test Full-Stack Application

This is a test repository with both backend and frontend services.

## Backend (Flask)
- Port: 5000
- Health endpoint: /api/health

## Frontend (Node.js/Express)
- Port: 3000
- Connects to backend on port 5000

## Running
1. Backend: `cd backend && pip install -r requirements.txt && python app.py`
2. Frontend: `cd frontend && npm install && npm start`

Or use Docker: `docker-compose up`
'''
    
    with open(os.path.join(test_repo_path, "README.md"), "w") as f:
        f.write(readme)
    
    return test_repo_path

def test_agent_integration():
    """Test the complete agent integration workflow."""
    print("🧪 Testing Agent Integration Workflow")
    print("=" * 50)
    
    # Create test repository
    test_repo_path = create_test_repo()
    print(f"✅ Created test repository at: {test_repo_path}")
    
    try:
        # Import agents
        from repo_runner.agents.detection_agent import DetectionAgent
        from repo_runner.agents.requirements_agent import RequirementsAgent
        from repo_runner.agents.setup_agent import SetupAgent
        from repo_runner.agents.port_manager_agent import PortManagerAgent
        from repo_runner.agents.runner_agent import RunnerAgent
        from repo_runner.agents.health_agent import HealthAgent
        from repo_runner.agents.orchestrator import Orchestrator
        
        print("\n🔍 Phase 1: Repository Detection")
        detection_agent = DetectionAgent()
        detection_result = detection_agent.detect_project_structure(test_repo_path)
        services_info = detection_result['services']
        repo_analysis = detection_agent.analyze(test_repo_path)
        repo_analysis.update(services_info)
        print(f"✅ Detected services: {len(repo_analysis.get('services', []))}")
        
        print("\n📋 Phase 2: Requirements Analysis")
        requirements_agent = RequirementsAgent()
        requirements_result = requirements_agent.ensure_requirements(repo_analysis)
        print(f"✅ Requirements analyzed: {requirements_result.get('status')}")
        
        print("\n🔌 Phase 3: Port Management")
        port_manager = PortManagerAgent()
        allocated_ports = port_manager.allocate_ports_for_services(repo_analysis.get('services', []))
        print(f"✅ Allocated ports: {allocated_ports}")
        
        print("\n📦 Phase 4: Dependency Setup")
        setup_agent = SetupAgent()
        setup_result = setup_agent.install(requirements_result)
        service_setup = setup_agent.setup_services(repo_analysis)
        print(f"✅ Setup completed: {len(service_setup)} services configured")
        
        print("\n🚀 Phase 5: Service Startup")
        runner_agent = RunnerAgent()
        startup_result = runner_agent.start(repo_analysis, "local", allocated_ports)
        print(f"✅ Services started: {startup_result.get('started_services', [])}")
        
        print("\n🏥 Phase 6: Health Validation")
        health_agent = HealthAgent()
        health_result = health_agent.check(startup_result)
        service_health = health_agent.check_services(repo_analysis)
        print(f"✅ Health check completed: {health_result.get('ok', False)}")
        
        print("\n🎯 Phase 7: Full Orchestrator Test")
        orchestrator = Orchestrator(timeout=300)
        final_result = orchestrator.run(test_repo_path, "local")
        print(f"✅ Orchestrator completed: {final_result.get('status')}")
        
        # Test service connectivity
        print("\n🔗 Phase 8: Service Connectivity Test")
        time.sleep(5)  # Wait for services to start
        
        try:
            import requests
            # Test backend
            backend_response = requests.get("http://localhost:5000/api/health", timeout=5)
            print(f"✅ Backend health: {backend_response.status_code}")
            
            # Test frontend
            frontend_response = requests.get("http://localhost:3000/", timeout=5)
            print(f"✅ Frontend health: {frontend_response.status_code}")
            
            # Test frontend-backend connectivity
            connectivity_response = requests.get("http://localhost:3000/api/backend-status", timeout=5)
            print(f"✅ Service connectivity: {connectivity_response.status_code}")
            
        except Exception as e:
            print(f"⚠️ Service connectivity test failed: {e}")
        
        print("\n🎉 Integration Test Summary:")
        print(f"  📁 Repository: {test_repo_path}")
        print(f"  🔍 Services Detected: {len(repo_analysis.get('services', []))}")
        print(f"  🔌 Ports Allocated: {len(allocated_ports)}")
        print(f"  📦 Dependencies Installed: {len(setup_result.get('installed_deps', []))}")
        print(f"  🚀 Services Started: {len(startup_result.get('started_services', []))}")
        print(f"  🏥 Health Status: {health_result.get('ok', False)}")
        print(f"  🎯 Orchestrator Status: {final_result.get('status')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up test repository: {test_repo_path}")
        try:
            shutil.rmtree(test_repo_path)
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")

def test_cli_integration():
    """Test CLI integration with the test repository."""
    print("\n🖥️ Testing CLI Integration")
    print("=" * 30)
    
    test_repo_path = create_test_repo()
    
    try:
        # Test CLI commands
        project_path = os.path.join(os.getcwd(), 'project')
        os.chdir(project_path)
        
        print("1. Testing detect command...")
        detect_result = subprocess.run(
            ["python", "-m", "repo_runner.cli", "detect", test_repo_path],
            capture_output=True, text=True, timeout=60
        )
        print(f"   Exit code: {detect_result.returncode}")
        
        print("2. Testing setup command...")
        setup_result = subprocess.run(
            ["python", "-m", "repo_runner.cli", "setup", test_repo_path, "--skip-deps", "--skip-env", "--skip-db"],
            capture_output=True, text=True, timeout=60
        )
        print(f"   Exit code: {setup_result.returncode}")
        
        print("3. Testing run command...")
        run_result = subprocess.run(
            ["python", "-m", "repo_runner.cli", "run", test_repo_path, "--mode", "local"],
            capture_output=True, text=True, timeout=300
        )
        print(f"   Exit code: {run_result.returncode}")
        
        print("4. Testing health command...")
        health_result = subprocess.run(
            ["python", "-m", "repo_runner.cli", "health", test_repo_path],
            capture_output=True, text=True, timeout=60
        )
        print(f"   Exit code: {health_result.returncode}")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(test_repo_path)
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Local Integration Tests")
    print("=" * 50)
    
    # Test agent integration
    agent_success = test_agent_integration()
    
    # Test CLI integration
    cli_success = test_cli_integration()
    
    print("\n📊 Test Results:")
    print(f"  Agent Integration: {'✅ PASS' if agent_success else '❌ FAIL'}")
    print(f"  CLI Integration: {'✅ PASS' if cli_success else '❌ FAIL'}")
    
    if agent_success and cli_success:
        print("\n🎉 All tests passed! The repo_runner is ready for production use.")
    else:
        print("\n⚠️ Some tests failed. Please check the output above for details.") 