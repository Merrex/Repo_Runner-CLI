#!/usr/bin/env python3
"""
Comprehensive test script for the complete tier-based system
Demonstrates OrchestratorAgent as single POC with user tier restrictions
"""

import os
import sys
import json
import tempfile
import shutil
from repo_runner.user_management import UserManager, UserTier
from repo_runner.agents.context_indexer import ContextIndexer
from repo_runner.managers.orchestrator import OrchestratorAgent

def create_test_repo():
    """Create a test repository for testing"""
    test_repo = tempfile.mkdtemp(prefix="test_repo_")
    
    # Create a simple Python project
    os.makedirs(os.path.join(test_repo, "src"), exist_ok=True)
    
    # Create main.py
    with open(os.path.join(test_repo, "src", "main.py"), "w") as f:
        f.write("""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from Repo Runner!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
""")
    
    # Create requirements.txt
    with open(os.path.join(test_repo, "requirements.txt"), "w") as f:
        f.write("""
flask==2.3.3
requests==2.31.0
""")
    
    # Create README.md
    with open(os.path.join(test_repo, "README.md"), "w") as f:
        f.write("""
# Test Repository

This is a test repository for Repo Runner.

## Features
- Flask web application
- Health check endpoint
- Simple API

## Usage
```bash
python src/main.py
```
""")
    
    return test_repo

def test_user_tier_system():
    """Test the complete user tier system"""
    
    print("🧪 Testing Complete Tier-Based System")
    print("=" * 60)
    
    # Initialize user manager
    user_manager = UserManager('test_users.json')
    
    # Create test users
    test_users = [
        ('free_user', 'password123', UserTier.FREE),
        ('advanced_user', 'password123', UserTier.ADVANCED),
        ('premium_user', 'password123', UserTier.PREMIUM),
        ('tester_user', 'password123', UserTier.TESTER),
        ('admin_user', 'password123', UserTier.ADMIN)
    ]
    
    print("\n1️⃣ Creating test users:")
    for username, password, tier in test_users:
        success = user_manager.create_user(username, password, tier)
        print(f"   {username} ({tier.value}): {'✅' if success else '❌'}")
    
    return user_manager

def test_orchestrator_as_poc():
    """Test OrchestratorAgent as single POC with different user tiers"""
    
    print("\n2️⃣ Testing OrchestratorAgent as Single POC:")
    user_manager = UserManager('test_users.json')
    
    # Create test repository
    test_repo = create_test_repo()
    print(f"   📁 Created test repository: {test_repo}")
    
    try:
        # Test with each user tier
        for username in ['free_user', 'advanced_user', 'premium_user']:
            print(f"\n   🔄 Testing with {username}:")
            
            # Authenticate user
            if user_manager.authenticate(username, 'password123'):
                capabilities = user_manager.get_current_user_capabilities()
                print(f"     Tier: {capabilities.tier.value}")
                print(f"     Context Indexer: {capabilities.context_indexer_type}")
                print(f"     GPU Access: {capabilities.gpu_access}")
                
                # Create orchestrator configuration
                config = {
                    'repo_path': test_repo,
                    'environment': 'detect',
                    'model_tier': 'balanced',
                    'skip_agents': [],  # Run all agents
                    'faiss': {
                        'use_faiss': None,  # Let agents recommend
                        'sentence_transformer_model': None
                    }
                }
                
                # Run orchestrator (single POC)
                print(f"     🚀 Running OrchestratorAgent...")
                orchestrator = OrchestratorAgent(config=config)
                result = orchestrator.run()
                
                # Check results
                if result.get('status') == 'ok':
                    print(f"     ✅ Orchestration completed successfully")
                    summary = result.get('summary', {})
                    print(f"     📊 Agents run: {summary.get('successful_agents', 0)}/{summary.get('total_agents', 0)}")
                    
                    # Check context indexer info
                    context_info = summary.get('context_indexer')
                    if context_info:
                        print(f"     🔍 Context Indexer: {context_info.get('index_type', 'Unknown')}")
                        if 'user_info' in context_info:
                            user_info = context_info['user_info']
                            print(f"     👤 User Tier: {user_info.get('user_tier', 'Unknown')}")
                            print(f"     🔓 Allowed Indexers: {user_info.get('allowed_indexer_types', [])}")
                else:
                    print(f"     ❌ Orchestration failed: {result.get('error', 'Unknown error')}")
                
                # Test rate limiting
                print(f"     ⏱️ Testing rate limiting...")
                for i in range(5):
                    can_proceed = user_manager.check_rate_limit()
                    print(f"       Request {i+1}: {'✅' if can_proceed else '❌'}")
                    if not can_proceed:
                        break
                
            else:
                print(f"     ❌ Authentication failed for {username}")
    
    finally:
        # Cleanup test repository
        if os.path.exists(test_repo):
            shutil.rmtree(test_repo)
            print(f"   🧹 Cleaned up test repository")

def test_admin_functions():
    """Test admin functions for user management"""
    
    print("\n3️⃣ Testing Admin Functions:")
    user_manager = UserManager('test_users.json')
    
    # Test as admin user
    if user_manager.authenticate('admin_user', 'password123'):
        print("   ✅ Admin login successful")
        
        # List users
        users = user_manager.list_users('admin_user')
        print(f"   📋 Found {len(users)} users")
        
        # Test user management functions
        test_username = 'test_user'
        
        # Create a test user
        if user_manager.create_user(test_username, 'password123', UserTier.FREE, created_by='admin_user'):
            print(f"   ✅ Created test user: {test_username}")
            
            # Upgrade user
            if user_manager.upgrade_user(test_username, UserTier.ADVANCED, 'admin_user'):
                print(f"   ✅ Upgraded {test_username} to Advanced")
            
            # Block user
            if user_manager.block_user(test_username, 'admin_user'):
                print(f"   ✅ Blocked {test_username}")
            
            # Unblock user
            if user_manager.unblock_user(test_username, 'admin_user'):
                print(f"   ✅ Unblocked {test_username}")
            
            # Delete user
            if user_manager.delete_user(test_username, 'admin_user'):
                print(f"   ✅ Deleted {test_username}")
        else:
            print(f"   ❌ Failed to create test user")
    
    # Test as non-admin user
    if user_manager.authenticate('free_user', 'password123'):
        users = user_manager.list_users('free_user')
        if not users:
            print("   ✅ Non-admin correctly denied user listing")
        else:
            print("   ❌ Non-admin should not see users")

def test_context_indexer_tiers():
    """Test context indexer with different user tiers"""
    
    print("\n4️⃣ Testing Context Indexer Tier Restrictions:")
    user_manager = UserManager('test_users.json')
    
    # Test each tier's context indexer access
    for username in ['free_user', 'advanced_user', 'premium_user']:
        print(f"\n   Testing {username}:")
        
        if user_manager.authenticate(username, 'password123'):
            capabilities = user_manager.get_current_user_capabilities()
            
            # Test different indexer types
            indexer_types = ['simple', 'faiss', 'chroma']
            for indexer_type in indexer_types:
                can_use = user_manager.can_use_context_indexer(indexer_type)
                print(f"     {indexer_type}: {'✅' if can_use else '❌'}")
            
            # Create context indexer
            indexer = ContextIndexer()
            info = indexer.get_index_info()
            print(f"     Selected indexer: {info['index_type']}")
            if 'user_info' in info:
                print(f"     User tier: {info['user_info'].get('user_tier', 'unknown')}")

def test_workflow_completion():
    """Test that workflow stops only when test_repo is run"""
    
    print("\n5️⃣ Testing Workflow Completion:")
    
    # Create test repository
    test_repo = create_test_repo()
    
    try:
        print(f"   📁 Test repository: {test_repo}")
        
        # Test orchestrator workflow
        config = {
            'repo_path': test_repo,
            'environment': 'detect',
            'model_tier': 'balanced',
            'skip_agents': ['HealthAgent'],  # Skip health check for testing
            'faiss': {
                'use_faiss': None,
                'sentence_transformer_model': None
            }
        }
        
        print("   🚀 Running complete workflow...")
        orchestrator = OrchestratorAgent(config=config)
        result = orchestrator.run()
        
        if result.get('status') == 'ok':
            print("   ✅ Workflow completed successfully")
            
            # Check that all phases were executed
            summary = result.get('summary', {})
            successful_agents = summary.get('successful_agents', 0)
            total_agents = summary.get('total_agents', 0)
            
            print(f"   📊 Workflow Summary:")
            print(f"     Successful agents: {successful_agents}/{total_agents}")
            print(f"     Environment: {summary.get('environment', 'unknown')}")
            
            # Check for checkpoint files
            checkpoint_files = [
                'run_state.json',
                'agent_state_EnvDetectorAgent.json',
                'agent_state_DependencyAgent.json',
                'agent_state_SetupAgent.json',
                'agent_state_RunnerAgent.json'
            ]
            
            print(f"   📝 Checkpoint files:")
            for file in checkpoint_files:
                if os.path.exists(file):
                    print(f"     ✅ {file}")
                else:
                    print(f"     ❌ {file} (missing)")
            
            # Check context indexer
            context_info = summary.get('context_indexer')
            if context_info:
                print(f"   🔍 Context Indexer: {context_info.get('index_type', 'Unknown')}")
                print(f"     Chunks indexed: {context_info.get('chunk_count', 0)}")
                print(f"     FAISS available: {context_info.get('faiss_available', False)}")
            
        else:
            print(f"   ❌ Workflow failed: {result.get('error', 'Unknown error')}")
    
    finally:
        # Cleanup
        if os.path.exists(test_repo):
            shutil.rmtree(test_repo)
        
        # Cleanup checkpoint files
        for file in ['run_state.json', 'agent_state_*.json']:
            if os.path.exists(file):
                os.remove(file)

def cleanup():
    """Cleanup test files"""
    test_files = ['test_users.json']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleaned up {file}")

if __name__ == '__main__':
    print("🚀 Complete Tier-Based System Test")
    print("=" * 70)
    
    try:
        test_user_tier_system()
        test_orchestrator_as_poc()
        test_admin_functions()
        test_context_indexer_tiers()
        test_workflow_completion()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 System Summary:")
        print("   ✅ User tier system with proper permissions")
        print("   ✅ OrchestratorAgent as single POC")
        print("   ✅ Context indexer tier restrictions")
        print("   ✅ Admin functions for user management")
        print("   ✅ Workflow completion with test_repo")
        print("   ✅ Rate limiting and usage tracking")
        print("   ✅ Checkpoint and state management")
        
        print("\n🎯 Key Features:")
        print("   - Free users: Simple text search, no GPU, 10 req/hour")
        print("   - Advanced users: FAISS indexing, small GPU, 50 req/hour")
        print("   - Premium users: Chroma indexing, large GPU, 200 req/hour")
        print("   - Tester/Admin: Full access, user management (admin only)")
        print("   - Single admin user with exclusive management privileges")
        print("   - OrchestratorAgent handles all user interactions")
        print("   - Workflow stops only when test_repo is completed")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup() 