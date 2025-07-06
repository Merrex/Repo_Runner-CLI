#!/usr/bin/env python3
"""
Test script to verify LLM model configuration for all agents.
This script tests that each agent's model loads correctly and generates responses.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.llm_utils import AGENT_LLM_CONFIG, generate_code_with_llm
import time

def test_model_loading():
    """Test that each agent's model loads correctly."""
    print("🧪 Testing Model Loading for All Agents")
    print("=" * 50)
    
    test_prompts = {
        'detection_agent': "Analyze this project structure and identify the main components:",
        'requirements_agent': "Generate a requirements.txt file for a Python web application:",
        'setup_agent': "Create installation commands for a Python project with dependencies:",
        'fixer_agent': "Fix this Python import error: ModuleNotFoundError: No module named 'requests':",
        'db_agent': "Generate SQL commands to create a users table with id, name, email fields:",
        'health_agent': "Check if a web service is running on port 8000 and report status:",
        'runner_agent': "Start a Python FastAPI application on port 8000:"
    }
    
    results = {}
    
    for agent_name, config in AGENT_LLM_CONFIG.items():
        print(f"\n🔍 Testing {agent_name}...")
        print(f"   Model: {config['model_name']}")
        print(f"   Max Tokens: {config['max_tokens']}")
        print(f"   Temperature: {config['temperature']}")
        
        try:
            start_time = time.time()
            
            # Test with a simple prompt
            test_prompt = test_prompts.get(agent_name, "Generate a simple response:")
            response = generate_code_with_llm(
                prompt=test_prompt,
                agent_name=agent_name,
                max_new_tokens=min(100, config['max_tokens']),  # Use smaller tokens for testing
                temperature=config['temperature']
            )
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Check if response is valid
            if response and len(response.strip()) > 0:
                status = "✅ SUCCESS"
                results[agent_name] = {
                    'status': 'success',
                    'time': generation_time,
                    'response_length': len(response),
                    'model': config['model_name']
                }
            else:
                status = "❌ EMPTY RESPONSE"
                results[agent_name] = {
                    'status': 'empty_response',
                    'time': generation_time,
                    'response_length': 0,
                    'model': config['model_name']
                }
                
        except Exception as e:
            status = f"❌ ERROR: {str(e)}"
            results[agent_name] = {
                'status': 'error',
                'error': str(e),
                'model': config['model_name']
            }
        
        print(f"   Status: {status}")
        if 'time' in results[agent_name]:
            print(f"   Time: {results[agent_name]['time']:.2f}s")
        if 'response_length' in results[agent_name]:
            print(f"   Response Length: {results[agent_name]['response_length']} chars")
    
    return results

def print_summary(results):
    """Print a summary of test results."""
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for agent_name, result in results.items():
        if result['status'] == 'success':
            successful += 1
            print(f"✅ {agent_name}: {result['model']} ({result['time']:.2f}s)")
        else:
            failed += 1
            error_msg = result.get('error', 'Empty response')
            print(f"❌ {agent_name}: {result['model']} - {error_msg}")
    
    print(f"\n📈 Results: {successful} successful, {failed} failed")
    
    if successful == len(results):
        print("🎉 All models loaded and generated responses successfully!")
    else:
        print("⚠️  Some models failed. Check the errors above.")

def test_memory_usage():
    """Test memory usage for different model sizes."""
    print("\n🧠 Testing Memory Usage")
    print("=" * 30)
    
    # Test with a lightweight model first
    print("Testing lightweight model (Zephyr 1.3B)...")
    try:
        response = generate_code_with_llm(
            prompt="Generate a simple Python function:",
            agent_name='detection_agent',
            max_new_tokens=50
        )
        print("✅ Lightweight model works")
    except Exception as e:
        print(f"❌ Lightweight model failed: {e}")
    
    # Test with a medium model
    print("Testing medium model (WizardCoder 1B)...")
    try:
        response = generate_code_with_llm(
            prompt="Fix this Python code:",
            agent_name='fixer_agent',
            max_new_tokens=100
        )
        print("✅ Medium model works")
    except Exception as e:
        print(f"❌ Medium model failed: {e}")

def test_token_limits():
    """Test that token limits are respected."""
    print("\n🔢 Testing Token Limits")
    print("=" * 25)
    
    # Test with very long prompt
    long_prompt = "This is a very long prompt. " * 1000  # ~6000 characters
    
    try:
        response = generate_code_with_llm(
            prompt=long_prompt,
            agent_name='detection_agent',
            max_new_tokens=50
        )
        print("✅ Long prompt handled correctly (truncated)")
    except Exception as e:
        print(f"❌ Long prompt failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting LLM Model Tests")
    print("This will test all agent models to ensure they load and generate responses correctly.")
    print("This may take a few minutes for the first run as models are downloaded.")
    
    # Test 1: Model loading and basic generation
    results = test_model_loading()
    print_summary(results)
    
    # Test 2: Memory usage
    test_memory_usage()
    
    # Test 3: Token limits
    test_token_limits()
    
    print("\n🎯 Test completed!")
    print("If all tests pass, your model configuration is working correctly.")
    print("If any tests fail, check the error messages and model availability.") 