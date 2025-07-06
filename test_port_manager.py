#!/usr/bin/env python3
"""
Test script for port manager functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repo_runner.agents.port_manager_agent import PortManagerAgent

def test_port_manager():
    """Test the port manager agent functionality."""
    print("🧪 Testing Port Manager Agent...")
    
    # Create port manager instance
    port_manager = PortManagerAgent()
    
    # Test port availability checking
    print("\n1. Testing port availability...")
    port_8000_available = port_manager.check_port_availability(8000)
    port_3000_available = port_manager.check_port_availability(3000)
    print(f"Port 8000 available: {port_8000_available}")
    print(f"Port 3000 available: {port_3000_available}")
    
    # Test finding free ports
    print("\n2. Testing free port finding...")
    free_backend_port = port_manager.find_free_port(8000, 8010)
    free_frontend_port = port_manager.find_free_port(3000, 3010)
    print(f"Free backend port: {free_backend_port}")
    print(f"Free frontend port: {free_frontend_port}")
    
    # Test service port allocation
    print("\n3. Testing service port allocation...")
    mock_services = [
        {'type': 'python', 'role': 'backend', 'path': '/test/backend'},
        {'type': 'node', 'role': 'frontend', 'path': '/test/frontend'},
        {'type': 'docker', 'role': 'db', 'path': '/test/db'}
    ]
    
    allocated_ports = port_manager.allocate_ports_for_services(mock_services)
    print(f"Allocated ports: {allocated_ports}")
    
    # Test port configuration
    print("\n4. Testing port configuration...")
    port_config = port_manager.get_port_configuration(mock_services)
    print(f"Port configuration: {port_config}")
    
    # Test port status checking
    print("\n5. Testing port status checking...")
    port_status = port_manager.check_service_ports(mock_services)
    print(f"Port status: {port_status}")
    
    # Test port validation
    print("\n6. Testing port validation...")
    is_valid, errors = port_manager.validate_port_configuration(allocated_ports)
    print(f"Port configuration valid: {is_valid}")
    print(f"Validation errors: {errors}")
    
    print("\n✅ Port Manager Agent test completed successfully!")

if __name__ == "__main__":
    test_port_manager() 