#!/usr/bin/env python3
"""
Test script to verify the fixes for the repo_runner issues
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add repo_runner to path
sys.path.insert(0, str(Path(__file__).parent))

def create_test_repo():
    """Create a simple test repository"""
    test_dir = tempfile.mkdtemp(prefix="test_repo_")
    
    # Create a simple package.json
    package_json = {
        "name": "test-app",
        "version": "1.0.0",
        "scripts": {
            "start": "node server.js",
            "dev": "node server.js"
        },
        "dependencies": {
            "express": "^4.17.1"
        }
    }
    
    # Create server.js
    server_js = """
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.json({ message: 'Hello from test server!' });
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
"""
    
    # Write files
    import json
    with open(os.path.join(test_dir, 'package.json'), 'w') as f:
        json.dump(package_json, f, indent=2)
    
    with open(os.path.join(test_dir, 'server.js'), 'w') as f:
        f.write(server_js)
    
    return test_dir

def test_health_agent_fix():
    """Test that health agent doesn't crash with string input"""
    print("🧪 Testing health agent fix...")
    
    try:
        from repo_runner.agents.health_agent import HealthAgent
        
        health_agent = HealthAgent()
        
        # Test with string input (should not crash)
        result = health_agent.check("test_path")
        print(f"✅ Health agent handled string input: {result}")
        
        # Test with proper dict input
        mock_status = {
            'status': 'running',
            'started_services': ['node'],
            'processes': [{'type': 'node', 'pid': 12345}],
            'urls': ['http://localhost:3000']
        }
        
        result = health_agent.check(mock_status)
        print(f"✅ Health agent handled dict input: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health agent test failed: {e}")
        return False

def test_port_manager_cleanup():
    """Test port manager cleanup functionality"""
    print("🧪 Testing port manager cleanup...")
    
    try:
        from repo_runner.agents.port_manager_agent import EnvironmentAwarePortManager
        
        port_manager = EnvironmentAwarePortManager()
        
        # Test cleanup (should not crash)
        port_manager.cleanup_tunnels()
        print("✅ Port manager cleanup worked")
        
        return True
        
    except Exception as e:
        print(f"❌ Port manager cleanup test failed: {e}")
        return False

def test_service_detection():
    """Test service detection with proper error handling"""
    print("🧪 Testing service detection...")
    
    try:
        from repo_runner.managers.orchestrator import AutonomousServiceOrchestrator
        from repo_runner.managers.port_manager import EnvironmentAwarePortManager
        
        orchestrator = AutonomousServiceOrchestrator()
        
        # Test with non-existent service path
        result = orchestrator.start_service(
            "test_service",
            {
                'path': './nonexistent',
                'type': 'node',
                'framework': 'express',
                'role': 'backend'
            },
            "/tmp"
        )
        
        print(f"✅ Service start handled missing path: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service detection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing repo_runner fixes...")
    print("=" * 50)
    
    tests = [
        test_health_agent_fix,
        test_port_manager_cleanup,
        test_service_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All fixes are working correctly!")
        return 0
    else:
        print("❌ Some fixes need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 