#!/usr/bin/env python3
"""
CLI interface for repo_runner.
"""

import argparse
import sys
import os
from .orchestrator import OrchestratorAgent
from .config_manager import ConfigManager
from .user_management import get_user_manager, UserTier

def main():
    parser = argparse.ArgumentParser(description='Repo Runner CLI - Agentic Microservice Backend')
    
    # Authentication
    parser.add_argument('--username', type=str, help='Username for authentication')
    parser.add_argument('--password', type=str, help='Password for authentication')
    parser.add_argument('--login', action='store_true', help='Login with username/password')
    parser.add_argument('--register', action='store_true', help='Register new user')
    parser.add_argument('--tier', type=str, choices=['free', 'advanced', 'premium', 'tester', 'admin'],
                       default='free', help='User tier for registration')
    
    # Core CLI parameters
    parser.add_argument('--repo_path', type=str, default='.', 
                       help='Path to the repository to analyze and run')
    parser.add_argument('--env', type=str, default='detect', 
                       choices=['detect', 'colab', 'aws', 'gcp', 'local'],
                       help='Environment to run in (detect=auto-detect)')
    parser.add_argument('--model', type=str, default='tier', 
                       choices=['premium', 'free', 'balanced', 'tier'],
                       help='Model tier to use (tier=auto-select based on env)')
    
    # FAISS configuration (tier-restricted)
    parser.add_argument('--use_faiss', type=str, default=None,
                       choices=['true', 'false', 'auto'],
                       help='FAISS usage: true=force FAISS, false=force simple search, auto=agent recommendation')
    parser.add_argument('--faiss_model', type=str, default=None,
                       help='Sentence transformer model for FAISS (e.g., all-MiniLM-L6-v2)')
    
    # Advanced options
    parser.add_argument('--config_file', type=str, default=None,
                       help='Path to configuration file')
    parser.add_argument('--log_level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--checkpoint_dir', type=str, default='./checkpoints',
                       help='Directory for agent checkpoints')
    parser.add_argument('--skip_agents', nargs='*', default=[],
                       help='Skip specific agents (e.g., --skip_agents EnvDetectorAgent DependencyAgent)')
    
    # Admin commands
    parser.add_argument('--list_users', action='store_true', help='List all users (admin only)')
    parser.add_argument('--upgrade_user', type=str, help='Upgrade user tier (admin only)')
    parser.add_argument('--new_tier', type=str, choices=['free', 'advanced', 'premium', 'tester', 'admin'],
                       help='New tier for user upgrade')
    parser.add_argument('--block_user', type=str, help='Block a user (admin only)')
    parser.add_argument('--unblock_user', type=str, help='Unblock a user (admin only)')
    parser.add_argument('--delete_user', type=str, help='Delete a user (admin only)')
    parser.add_argument('--usage', action='store_true', help='Show current user usage')
    
    args = parser.parse_args()
    
    # Initialize user manager
    user_manager = get_user_manager()
    
    # Handle authentication commands
    if args.login:
        if not args.username or not args.password:
            print("❌ --login requires both --username and --password")
            sys.exit(1)
        
        if user_manager.authenticate(args.username, args.password):
            print(f"✅ Logged in as {args.username}")
        else:
            print("❌ Authentication failed")
            sys.exit(1)
    
    elif args.register:
        if not args.username or not args.password:
            print("❌ --register requires both --username and --password")
            sys.exit(1)
        
        tier = UserTier(args.tier)
        if user_manager.create_user(args.username, args.password, tier):
            print(f"✅ Registered {args.username} as {tier.value} user")
            if user_manager.authenticate(args.username, args.password):
                print(f"✅ Logged in as {args.username}")
        else:
            print("❌ Registration failed")
            sys.exit(1)
    
    elif args.list_users:
        if not user_manager.current_user:
            print("❌ Must be logged in to list users")
            sys.exit(1)
        
        users = user_manager.list_users(user_manager.current_user)
        if users:
            print("\n👥 Users:")
            for user in users:
                status_icon = "🟢" if user['status'] == 'active' else "🔴" if user['status'] == 'blocked' else "⚫"
                print(f"  {status_icon} {user['username']} ({user['tier']}) - Status: {user['status']} - Created: {user['created_at']}")
        else:
            print("❌ No users found or insufficient permissions")
    
    elif args.upgrade_user:
        if not user_manager.current_user:
            print("❌ Must be logged in to upgrade users")
            sys.exit(1)
        
        if not args.new_tier:
            print("❌ --upgrade_user requires --new_tier")
            sys.exit(1)
        
        new_tier = UserTier(args.new_tier)
        if user_manager.upgrade_user(args.upgrade_user, new_tier, user_manager.current_user):
            print(f"✅ Upgraded {args.upgrade_user} to {new_tier.value}")
        else:
            print("❌ User upgrade failed")
            sys.exit(1)
    
    elif args.block_user:
        if not user_manager.current_user:
            print("❌ Must be logged in to block users")
            sys.exit(1)
        
        if user_manager.block_user(args.block_user, user_manager.current_user):
            print(f"✅ Blocked user: {args.block_user}")
        else:
            print("❌ User blocking failed")
            sys.exit(1)
    
    elif args.unblock_user:
        if not user_manager.current_user:
            print("❌ Must be logged in to unblock users")
            sys.exit(1)
        
        if user_manager.unblock_user(args.unblock_user, user_manager.current_user):
            print(f"✅ Unblocked user: {args.unblock_user}")
        else:
            print("❌ User unblocking failed")
            sys.exit(1)
    
    elif args.delete_user:
        if not user_manager.current_user:
            print("❌ Must be logged in to delete users")
            sys.exit(1)
        
        if user_manager.delete_user(args.delete_user, user_manager.current_user):
            print(f"✅ Deleted user: {args.delete_user}")
        else:
            print("❌ User deletion failed")
            sys.exit(1)
    
    elif args.usage:
        if not user_manager.current_user:
            print("❌ Must be logged in to view usage")
            sys.exit(1)
        
        usage = user_manager.get_usage_summary()
        if usage:
            print(f"\n📊 Usage Summary for {usage['username']}:")
            print(f"  Tier: {usage['tier']}")
            print(f"  Status: {usage['status']}")
            print(f"  Support Level: {usage['support_level']}")
            print(f"  GPU Access: {usage['capabilities']['gpu_access']}")
            print(f"  GPU Size: {usage['capabilities']['gpu_size']}")
            print(f"  Context Indexer: {usage['capabilities']['context_indexer_type']}")
            print(f"  Rate Limit: {usage['capabilities']['rate_limit_per_hour']}/hour")
            print(f"  Repos Created: {usage['usage']['repos_created']}")
            print(f"  Agents Used: {usage['usage']['agents_used']}")
            print(f"  Requests This Hour: {usage['usage']['requests_this_hour']}")
    
    else:
        # Main workflow - check authentication
        if not user_manager.current_user:
            print("⚠️ Not logged in - using free tier with limited features")
            print("💡 Use --login or --register to access advanced features")
        
        # Check rate limit
        if not user_manager.check_rate_limit():
            print("❌ Rate limit exceeded. Please wait or upgrade your tier.")
            sys.exit(1)
        
        # Convert FAISS string to boolean/None
        use_faiss = None
        if args.use_faiss == 'true':
            use_faiss = True
        elif args.use_faiss == 'false':
            use_faiss = False
        # 'auto' and None both result in None (agent recommendation)
        
        # Check FAISS permissions
        if use_faiss and not user_manager.can_use_context_indexer('faiss'):
            print("❌ FAISS not available for your tier. Upgrading to Advanced or higher required.")
            sys.exit(1)
        
        # Build configuration
        config = {
            'repo_path': args.repo_path,
            'environment': args.env,
            'model_tier': args.model,
            'log_level': args.log_level,
            'checkpoint_dir': args.checkpoint_dir,
            'skip_agents': args.skip_agents,
            'faiss': {
                'use_faiss': use_faiss,
                'sentence_transformer_model': args.faiss_model
            }
        }
        
        # Load config file if provided
        if args.config_file and os.path.exists(args.config_file):
            config_manager = ConfigManager()
            file_config = config_manager.load_config(args.config_file)
            config.update(file_config)
        
        # Initialize and run orchestrator
        try:
            orchestrator = OrchestratorAgent(config=config)
            result = orchestrator.run()
            
            # Increment usage
            user_manager.increment_usage('repo')
            
            if result.get('status') == 'ok':
                print("✅ Repo Runner completed successfully!")
                print(f"📊 Summary: {result.get('summary', 'No summary available')}")
            else:
                print(f"❌ Repo Runner failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()