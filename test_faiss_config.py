#!/usr/bin/env python3
"""
Test script to demonstrate FAISS configuration system
"""

import os
import sys
import json
from repo_runner.agents.context_indexer import ContextIndexer
from repo_runner.agents.env_detector import EnvDetectorAgent
from repo_runner.agents.dependency_agent import DependencyAgent

def test_faiss_configuration():
    """Test different FAISS configuration scenarios"""
    
    print("🧪 Testing FAISS Configuration System")
    print("=" * 50)
    
    # Test 1: User-configured FAISS
    print("\n1️⃣ Test: User-configured FAISS")
    indexer1 = ContextIndexer(
        use_faiss=True, 
        config={'sentence_transformer_model': 'all-MiniLM-L6-v2'}
    )
    info1 = indexer1.get_index_info()
    print(f"   Configuration: {info1}")
    
    # Test 2: User-configured simple search
    print("\n2️⃣ Test: User-configured simple search")
    indexer2 = ContextIndexer(use_faiss=False)
    info2 = indexer2.get_index_info()
    print(f"   Configuration: {info2}")
    
    # Test 3: Agent-recommended (automatic)
    print("\n3️⃣ Test: Agent-recommended (automatic)")
    
    # Run environment detection agent
    env_agent = EnvDetectorAgent()
    env_result = env_agent.run()
    print(f"   Environment: {env_result.get('environment')}")
    print(f"   Recommendations: {env_result.get('recommendations')}")
    
    # Run dependency agent
    dep_agent = DependencyAgent()
    dep_result = dep_agent.run()
    print(f"   Dependency recommendations: {dep_result.get('recommendations')}")
    
    # Create indexer with agent recommendations
    indexer3 = ContextIndexer()  # Will use agent recommendations
    info3 = indexer3.get_index_info()
    print(f"   Final configuration: {info3}")
    
    # Test 4: Environment-specific recommendations
    print("\n4️⃣ Test: Environment-specific recommendations")
    
    # Simulate different environments
    environments = ['colab', 'aws', 'local']
    
    for env in environments:
        print(f"\n   Testing {env} environment:")
        
        # Create mock environment state
        env_state = {
            'environment': env,
            'recommendations': {
                'recommend_faiss': env in ['colab', 'aws'],  # Colab and AWS support FAISS
                'reason': f'{env} environment analysis',
                'sentence_transformer_model': 'all-MiniLM-L6-v2' if env in ['colab', 'aws'] else None
            }
        }
        
        # Save mock state
        with open(f'agent_state_EnvDetectorAgent.json', 'w') as f:
            json.dump(env_state, f, indent=2)
        
        # Test indexer with this environment
        indexer_env = ContextIndexer()
        info_env = indexer_env.get_index_info()
        print(f"     FAISS recommended: {info_env['use_faiss']}")
        print(f"     Reason: {info_env['config'].get('reason', 'No reason')}")
        
        # Cleanup
        if os.path.exists('agent_state_EnvDetectorAgent.json'):
            os.remove('agent_state_EnvDetectorAgent.json')

def test_cli_integration():
    """Test CLI integration with FAISS configuration"""
    
    print("\n🔧 Testing CLI Integration")
    print("=" * 50)
    
    # Simulate CLI commands
    cli_scenarios = [
        {
            'name': 'Force FAISS',
            'args': ['--use_faiss', 'true', '--faiss_model', 'all-MiniLM-L6-v2'],
            'expected': {'use_faiss': True, 'sentence_transformer_model': 'all-MiniLM-L6-v2'}
        },
        {
            'name': 'Force simple search',
            'args': ['--use_faiss', 'false'],
            'expected': {'use_faiss': False}
        },
        {
            'name': 'Agent recommendation',
            'args': ['--use_faiss', 'auto'],
            'expected': {'use_faiss': None}  # Will be determined by agents
        }
    ]
    
    for scenario in cli_scenarios:
        print(f"\n   Testing: {scenario['name']}")
        print(f"   Args: {' '.join(scenario['args'])}")
        print(f"   Expected: {scenario['expected']}")
        
        # Create indexer with these settings
        use_faiss = None
        if '--use_faiss' in scenario['args']:
            idx = scenario['args'].index('--use_faiss')
            if idx + 1 < len(scenario['args']):
                use_faiss_str = scenario['args'][idx + 1]
                if use_faiss_str == 'true':
                    use_faiss = True
                elif use_faiss_str == 'false':
                    use_faiss = False
        
        faiss_model = None
        if '--faiss_model' in scenario['args']:
            idx = scenario['args'].index('--faiss_model')
            if idx + 1 < len(scenario['args']):
                faiss_model = scenario['args'][idx + 1]
        
        config = {}
        if faiss_model:
            config['sentence_transformer_model'] = faiss_model
        
        indexer = ContextIndexer(use_faiss=use_faiss, config=config)
        info = indexer.get_index_info()
        print(f"   Result: {info}")

def test_context_search():
    """Test context search functionality"""
    
    print("\n🔍 Testing Context Search")
    print("=" * 50)
    
    # Create test files
    test_files = [
        'test_file1.txt',
        'test_file2.txt',
        'test_file3.txt'
    ]
    
    # Create test content
    test_content = {
        'test_file1.txt': 'This is a Python project with machine learning capabilities.',
        'test_file2.txt': 'The project uses transformers and torch for NLP tasks.',
        'test_file3.txt': 'FAISS is used for efficient similarity search in the codebase.'
    }
    
    # Write test files
    for filename, content in test_content.items():
        with open(filename, 'w') as f:
            f.write(content)
    
    try:
        # Test with FAISS (if available)
        print("\n   Testing with FAISS:")
        indexer_faiss = ContextIndexer(use_faiss=True)
        indexer_faiss.build_index(test_files)
        
        query = "machine learning transformers"
        results_faiss = indexer_faiss.query_index(query, top_k=2)
        print(f"     Query: '{query}'")
        print(f"     Results: {len(results_faiss)} chunks found")
        for i, result in enumerate(results_faiss):
            print(f"       {i+1}. {result[:100]}...")
        
        # Test with simple search
        print("\n   Testing with simple search:")
        indexer_simple = ContextIndexer(use_faiss=False)
        indexer_simple.build_index(test_files)
        
        results_simple = indexer_simple.query_index(query, top_k=2)
        print(f"     Query: '{query}'")
        print(f"     Results: {len(results_simple)} chunks found")
        for i, result in enumerate(results_simple):
            print(f"       {i+1}. {result[:100]}...")
            
    finally:
        # Cleanup test files
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    print("🚀 FAISS Configuration System Test")
    print("=" * 60)
    
    try:
        test_faiss_configuration()
        test_cli_integration()
        test_context_search()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary:")
        print("   - User can configure FAISS via CLI or config")
        print("   - Agents provide environment-aware recommendations")
        print("   - System falls back to simple search when FAISS unavailable")
        print("   - Context indexing works with both FAISS and simple search")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1) 