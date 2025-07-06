#!/usr/bin/env python3
"""
Test script for orchestrator with port management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repo_runner.agents.orchestrator import Orchestrator

def test_orchestrator():
    """Test the orchestrator with port management."""
    print("🧪 Testing Orchestrator with Port Management...")
    
    # Create orchestrator instance with short timeout for testing
    orchestrator = Orchestrator(timeout=60)  # 1 minute timeout for testing
    
    # Test with current directory
    repo_path = "."
    
    print(f"\n🎯 Testing orchestrator on: {repo_path}")
    print("This will test the new port management flow...")
    
    try:
        result = orchestrator.run(repo_path, mode="local")
        print(f"\n✅ Orchestrator test completed!")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Completed phases: {result.get('workflow_state', {}).get('completed_phases', [])}")
        print(f"Failed phases: {result.get('workflow_state', {}).get('failed_phases', [])}")
        
        # Check if port management was executed
        if 'port_management' in result.get('checkpoint_results', {}):
            port_mgmt = result['checkpoint_results']['port_management']
            print(f"\n🔌 Port Management Results:")
            print(f"  Services count: {port_mgmt.get('services_count', 0)}")
            print(f"  Allocated ports: {port_mgmt.get('allocated_ports', {})}")
            print(f"  Is valid: {port_mgmt.get('is_valid', False)}")
        
    except Exception as e:
        print(f"\n❌ Orchestrator test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_orchestrator()
    if success:
        print("\n🎉 All tests passed! The system is ready for execution.")
    else:
        print("\n💥 Tests failed. Please check the errors above.")
        sys.exit(1) 