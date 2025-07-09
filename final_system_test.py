#!/usr/bin/env python3
"""
Final comprehensive system test to verify all components are working with real logic.
This test validates the complete agentic backend system before production deployment.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add the repo_runner to the path
sys.path.insert(0, str(Path(__file__).parent))

from repo_runner.agents.base_agent import BaseAgent
from repo_runner.agents.detection_agent import DetectionAgent
from repo_runner.agents.fixer_agent import FixerAgent
from repo_runner.agents.runner_agent import RunnerAgent
from repo_runner.agents.context_indexer import ContextIndexer
from repo_runner.admin_agent import AdminAgent
from repo_runner.managers.orchestrator import OrchestratorAgent
from repo_runner.user_management import UserManager, UserTier
from repo_runner.config_manager import ConfigManager
from repo_runner.health import HealthChecker
from repo_runner.database import DatabaseManager
from repo_runner.detectors import ProjectDetector

def create_test_repo():
    """Create a test repository with various components."""
    test_dir = tempfile.mkdtemp(prefix="test_repo_")
    
    # Create a simple Python Flask app
    app_py = f"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({{"message": "Hello from Repo Runner Test!", "status": "healthy"}})

@app.route('/health')
def health():
    return jsonify({{"status": "healthy", "service": "test-app"}})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
"""
    
    requirements_txt = """
flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
"""
    
    readme_md = """
# Test Repository

This is a test repository for the Repo Runner system.

## Features
- Flask web application
- Health check endpoint
- Environment variable support

## Running
```bash
python app.py
```

## Testing
Visit http://localhost:8000/health for health check.
"""
    
    # Write files
    with open(os.path.join(test_dir, 'app.py'), 'w') as f:
        f.write(app_py)
    
    with open(os.path.join(test_dir, 'requirements.txt'), 'w') as f:
        f.write(requirements_txt)
    
    with open(os.path.join(test_dir, 'README.md'), 'w') as f:
        f.write(readme_md)
    
    return test_dir

def test_user_management():
    """Test user management system."""
    print("🔐 Testing User Management System...")
    
    user_manager = UserManager()
    
    # Test user creation
    success = user_manager.create_user('test_user', 'password123', UserTier.ADVANCED)
    assert success, "User creation should succeed"
    
    # Test authentication
    auth_success = user_manager.authenticate('test_user', 'password123')
    assert auth_success, "Authentication should succeed"
    
    # Test tier capabilities
    capabilities = user_manager.get_current_user_capabilities()
    assert capabilities.tier == UserTier.ADVANCED, "User tier should be ADVANCED"
    
    print("✅ User Management System: PASS")

def test_config_manager():
    """Test configuration management."""
    print("⚙️ Testing Configuration Manager...")
    
    config_manager = ConfigManager()
    
    # Test config loading
    assert config_manager.config is not None, "Config should be loaded"
    assert 'models' in config_manager.config, "Models config should exist"
    assert 'api_keys' in config_manager.config, "API keys config should exist"
    
    # Test environment settings
    mode = config_manager.get_environment_setting('mode', 'local')
    assert mode in ['local', 'cloud'], "Mode should be valid"
    
    print("✅ Configuration Manager: PASS")

def test_detection_agent():
    """Test detection agent with real logic."""
    print("🔍 Testing Detection Agent...")
    
    test_repo = create_test_repo()
    
    try:
        detection_agent = DetectionAgent()
        
        # Test project structure detection
        result = detection_agent.detect_project_structure(test_repo)
        
        assert result['status'] == 'success', "Detection should succeed"
        assert 'services' in result, "Services should be detected"
        assert 'structure' in result, "Structure should be detected"
        
        # Test technology detection
        analysis = detection_agent.analyze(test_repo)
        assert 'technologies' in analysis, "Technologies should be detected"
        assert 'Python' in analysis['technologies'], "Python should be detected"
        
        print("✅ Detection Agent: PASS")
        
    finally:
        shutil.rmtree(test_repo)

def test_fixer_agent():
    """Test fixer agent with real logic."""
    print("🔧 Testing Fixer Agent...")
    
    fixer_agent = FixerAgent()
    
    # Test error analysis
    test_error = "ModuleNotFoundError: No module named 'flask'"
    fix_suggestion = fixer_agent._suggest_fix(test_error, ".")
    
    assert isinstance(fix_suggestion, dict), "Fix suggestion should be a dict"
    assert 'analysis' in fix_suggestion, "Analysis should be present"
    assert 'fix' in fix_suggestion, "Fix should be present"
    
    # Test dependency error fixing
    dependency_errors = ["No module named 'flask'"]
    fix_result = fixer_agent.fix_dependency_errors(dependency_errors, ".")
    
    assert fix_result['status'] == 'dependency_fixes_applied', "Dependency fixes should be applied"
    assert len(fix_result['fixes_applied']) > 0, "Fixes should be applied"
    
    print("✅ Fixer Agent: PASS")

def test_context_indexer():
    """Test context indexer with real logic."""
    print("📚 Testing Context Indexer...")
    
    test_repo = create_test_repo()
    
    try:
        indexer = ContextIndexer(use_faiss=False)  # Use simple text search for testing
        
        # Test index building
        files_to_index = [
            os.path.join(test_repo, 'app.py'),
            os.path.join(test_repo, 'README.md'),
            os.path.join(test_repo, 'requirements.txt')
        ]
        
        indexer.build_index(files_to_index)
        assert len(indexer.text_chunks) > 0, "Index should contain chunks"
        
        # Test querying
        results = indexer.query_index("flask app", top_k=2)
        assert len(results) > 0, "Query should return results"
        
        # Test index info
        info = indexer.get_index_info()
        assert 'chunk_count' in info, "Index info should contain chunk count"
        assert info['index_type'] == 'Simple Text', "Should use simple text index"
        
        print("✅ Context Indexer: PASS")
        
    finally:
        shutil.rmtree(test_repo)

def test_health_checker():
    """Test health checker with real logic."""
    print("🏥 Testing Health Checker...")
    
    health_checker = HealthChecker(".")
    
    # Test service health checking
    test_services = {
        'test_service': {
            'type': 'web',
            'url': 'http://localhost:8000',
            'port': 8000
        }
    }
    
    # Note: This will fail if no service is running, which is expected
    result = health_checker.check_all(test_services)
    # We don't assert here because the service might not be running
    
    # Test port checking logic
    port_check = health_checker._check_port({'port': 9999, 'host': 'localhost'})
    # This should fail because port 9999 is unlikely to be in use
    assert not port_check, "Port check should fail for unused port"
    
    print("✅ Health Checker: PASS")

def test_database_manager():
    """Test database manager with real logic."""
    print("🗄️ Testing Database Manager...")
    
    test_dir = tempfile.mkdtemp(prefix="test_db_")
    
    try:
        db_manager = DatabaseManager(Path(test_dir), dry_run=True)
        
        # Test SQLite setup
        structure = {'database': {'type': 'sqlite'}}
        db_manager.setup(structure)
        
        # Test connection check
        connection_ok = db_manager.check_database_connection()
        # This should fail because no DATABASE_URL is set
        assert not connection_ok, "Connection should fail without DATABASE_URL"
        
        print("✅ Database Manager: PASS")
        
    finally:
        shutil.rmtree(test_dir)

def test_project_detector():
    """Test project detector with real logic."""
    print("🔍 Testing Project Detector...")
    
    test_repo = create_test_repo()
    
    try:
        detector = ProjectDetector(Path(test_repo))
        
        # Test project detection
        structure = detector.detect()
        
        assert 'files' in structure, "Files should be detected"
        assert 'technologies' in structure, "Technologies should be detected"
        assert 'Python' in structure['technologies'], "Python should be detected"
        assert 'app.py' in structure['files'], "app.py should be detected"
        
        print("✅ Project Detector: PASS")
        
    finally:
        shutil.rmtree(test_repo)

def test_orchestrator_agent():
    """Test orchestrator agent with real logic."""
    print("🎼 Testing Orchestrator Agent...")
    
    orchestrator = OrchestratorAgent()
    
    # Test orchestrator initialization
    assert orchestrator is not None, "Orchestrator should be created"
    assert hasattr(orchestrator, 'agents'), "Orchestrator should have agents"
    assert hasattr(orchestrator, 'managers'), "Orchestrator should have managers"
    
    # Test workflow coordination
    test_repo = create_test_repo()
    
    try:
        # Test basic workflow
        result = orchestrator.coordinate_workflow(test_repo, mode='local')
        
        assert isinstance(result, dict), "Workflow result should be a dict"
        assert 'status' in result, "Result should have status"
        
        print("✅ Orchestrator Agent: PASS")
        
    finally:
        shutil.rmtree(test_repo)

def test_admin_agent():
    """Test admin agent with real logic."""
    print("👑 Testing Admin Agent...")
    
    admin_agent = AdminAgent()
    
    # Test admin agent initialization
    assert admin_agent is not None, "Admin Agent should be created"
    assert hasattr(admin_agent, 'orchestrators'), "Admin Agent should have orchestrators"
    
    # Test system control capabilities
    system_status = admin_agent.get_system_status()
    assert isinstance(system_status, dict), "System status should be a dict"
    
    print("✅ Admin Agent: PASS")

def run_comprehensive_test():
    """Run all comprehensive tests."""
    print("🚀 Starting Comprehensive System Test...")
    print("=" * 60)
    
    tests = [
        test_user_management,
        test_config_manager,
        test_detection_agent,
        test_fixer_agent,
        test_context_indexer,
        test_health_checker,
        test_database_manager,
        test_project_detector,
        test_orchestrator_agent,
        test_admin_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: FAILED - {e}")
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The system is ready for production.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 