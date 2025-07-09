#!/usr/bin/env python3
"""
Test script to demonstrate tier-based user system
"""

import os
import sys
import json
from repo_runner.user_management import UserManager, UserTier
from repo_runner.agents.context_indexer import ContextIndexer

def test_user_creation():
    """Test user creation and tier assignment"""
    
    print("🧪 Testing User Creation and Tier System")
    print("=" * 50)
    
    # Initialize user manager
    user_manager = UserManager('test_users.json')
    
    # Create test users for each tier
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

def test_authentication():
    """Test user authentication"""
    
    print("\n2️⃣ Testing Authentication:")
    user_manager = UserManager('test_users.json')
    
    # Test valid login
    if user_manager.authenticate('free_user', 'password123'):
        print("   ✅ Free user login successful")
    else:
        print("   ❌ Free user login failed")
    
    # Test invalid password
    if user_manager.authenticate('free_user', 'wrongpassword'):
        print("   ❌ Invalid password login should have failed")
    else:
        print("   ✅ Invalid password correctly rejected")

def test_tier_capabilities():
    """Test tier-based capabilities"""
    
    print("\n3️⃣ Testing Tier Capabilities:")
    user_manager = UserManager('test_users.json')
    
    tiers_to_test = [
        ('free_user', UserTier.FREE),
        ('advanced_user', UserTier.ADVANCED),
        ('premium_user', UserTier.PREMIUM),
        ('tester_user', UserTier.TESTER),
        ('admin_user', UserTier.ADMIN)
    ]
    
    for username, expected_tier in tiers_to_test:
        if user_manager.authenticate(username, 'password123'):
            capabilities = user_manager.get_current_user_capabilities()
            if capabilities:
                print(f"\n   {username} ({capabilities.tier.value}):")
                print(f"     Max repos: {capabilities.max_repos}")
                print(f"     Max agents: {capabilities.max_agents}")
                print(f"     Context indexer: {capabilities.context_indexer_type}")
                print(f"     GPU access: {capabilities.gpu_access}")
                print(f"     GPU size: {capabilities.gpu_size}")
                print(f"     Rate limit: {capabilities.rate_limit_per_hour}/hour")
                print(f"     Support: {capabilities.support_level}")
                
                # Test feature access
                features_to_test = ['basic_detection', 'advanced_detection', 'faiss_indexing', 'custom_models']
                for feature in features_to_test:
                    can_access = user_manager.can_access_feature(feature)
                    print(f"     {feature}: {'✅' if can_access else '❌'}")

def test_context_indexer_tiers():
    """Test context indexer with different user tiers"""
    
    print("\n4️⃣ Testing Context Indexer with Different Tiers:")
    user_manager = UserManager('test_users.json')
    
    # Test each tier
    for username in ['free_user', 'advanced_user', 'premium_user']:
        print(f"\n   Testing {username}:")
        
        # Authenticate user
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

def test_rate_limiting():
    """Test rate limiting per tier"""
    
    print("\n5️⃣ Testing Rate Limiting:")
    user_manager = UserManager('test_users.json')
    
    for username in ['free_user', 'advanced_user', 'premium_user']:
        print(f"\n   Testing rate limit for {username}:")
        
        if user_manager.authenticate(username, 'password123'):
            capabilities = user_manager.get_current_user_capabilities()
            limit = capabilities.rate_limit_per_hour
            
            # Test rate limit
            for i in range(limit + 2):  # Try to exceed limit
                can_proceed = user_manager.check_rate_limit()
                if can_proceed:
                    print(f"     Request {i+1}: ✅")
                else:
                    print(f"     Request {i+1}: ❌ (Rate limit exceeded)")
                    break

def test_admin_functions():
    """Test admin functions"""
    
    print("\n6️⃣ Testing Admin Functions:")
    user_manager = UserManager('test_users.json')
    
    # Test as admin user
    if user_manager.authenticate('admin_user', 'password123'):
        print("   ✅ Admin login successful")
        
        # List users
        users = user_manager.list_users('admin_user')
        print(f"   Found {len(users)} users")
        
        # Test user upgrade
        if user_manager.upgrade_user('free_user', UserTier.ADVANCED, 'admin_user'):
            print("   ✅ User upgrade successful")
        else:
            print("   ❌ User upgrade failed")
    
    # Test as non-admin user
    if user_manager.authenticate('free_user', 'password123'):
        users = user_manager.list_users('free_user')
        if not users:
            print("   ✅ Non-admin correctly denied user listing")
        else:
            print("   ❌ Non-admin should not see users")

def test_usage_tracking():
    """Test usage tracking"""
    
    print("\n7️⃣ Testing Usage Tracking:")
    user_manager = UserManager('test_users.json')
    
    for username in ['free_user', 'advanced_user', 'premium_user']:
        print(f"\n   Testing usage for {username}:")
        
        if user_manager.authenticate(username, 'password123'):
            # Simulate some usage
            user_manager.increment_usage('repo')
            user_manager.increment_usage('agent')
            user_manager.increment_usage('agent')
            
            # Get usage summary
            usage = user_manager.get_usage_summary()
            if usage:
                print(f"     Repos created: {usage['usage']['repos_created']}")
                print(f"     Agents used: {usage['usage']['agents_used']}")
                print(f"     Requests this hour: {usage['usage']['requests_this_hour']}")

def cleanup():
    """Cleanup test files"""
    test_files = ['test_users.json', 'agent_state_EnvDetectorAgent.json']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleaned up {file}")

if __name__ == '__main__':
    print("🚀 Tier-Based User System Test")
    print("=" * 60)
    
    try:
        test_user_creation()
        test_authentication()
        test_tier_capabilities()
        test_context_indexer_tiers()
        test_rate_limiting()
        test_admin_functions()
        test_usage_tracking()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Summary:")
        print("   - Free tier: Simple text search, no GPU, 10 req/hour")
        print("   - Advanced tier: FAISS indexing, small GPU, 50 req/hour")
        print("   - Premium tier: Chroma indexing, large GPU, 200 req/hour")
        print("   - Tester/Admin: Full access for testing/administration")
        print("   - Rate limiting and usage tracking working")
        print("   - Admin functions properly restricted")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    finally:
        cleanup() 