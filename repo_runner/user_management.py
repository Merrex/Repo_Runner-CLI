import os
import json
import hashlib
import time
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

class UserTier(Enum):
    """User tiers with different capabilities"""
    FREE = "free"
    ADVANCED = "advanced" 
    PREMIUM = "premium"
    TESTER = "tester"  # Internal testing (same privileges as admin except management)
    ADMIN = "admin"    # System administration (only one allowed)
    DEVELOPER = "developer"  # Can access Admin Agent (CEO of the system)

@dataclass
class UserCapabilities:
    """Capabilities for each user tier"""
    tier: UserTier
    max_repos: int
    max_agents: int
    context_indexer_type: str  # 'simple', 'faiss', 'chroma'
    gpu_access: bool
    gpu_size: str  # 'none', 'small', 'medium', 'large'
    advanced_features: List[str]
    rate_limit_per_hour: int
    support_level: str
    can_access_admin_agent: bool  # New field for Admin Agent access

class UserManager:
    """Manages user authentication, authorization, and tier-based access control"""
    
    # Tier capabilities configuration
    TIER_CAPABILITIES = {
        UserTier.FREE: UserCapabilities(
            tier=UserTier.FREE,
            max_repos=3,
            max_agents=5,
            context_indexer_type='simple',
            gpu_access=False,
            gpu_size='none',
            advanced_features=['basic_detection', 'simple_setup'],
            rate_limit_per_hour=10,
            support_level='community',
            can_access_admin_agent=False
        ),
        UserTier.ADVANCED: UserCapabilities(
            tier=UserTier.ADVANCED,
            max_repos=10,
            max_agents=10,
            context_indexer_type='faiss',
            gpu_access=True,
            gpu_size='small',
            advanced_features=['advanced_detection', 'faiss_indexing', 'health_monitoring'],
            rate_limit_per_hour=50,
            support_level='email',
            can_access_admin_agent=False
        ),
        UserTier.PREMIUM: UserCapabilities(
            tier=UserTier.PREMIUM,
            max_repos=100,
            max_agents=20,
            context_indexer_type='chroma',  # Best available
            gpu_access=True,
            gpu_size='large',
            advanced_features=['all_features', 'custom_models', 'priority_support'],
            rate_limit_per_hour=200,
            support_level='priority',
            can_access_admin_agent=False
        ),
        UserTier.TESTER: UserCapabilities(
            tier=UserTier.TESTER,
            max_repos=50,
            max_agents=15,
            context_indexer_type='faiss',  # Can test FAISS
            gpu_access=True,
            gpu_size='medium',
            advanced_features=['testing_features', 'beta_access', 'admin_features'],  # Same as admin
            rate_limit_per_hour=100,
            support_level='internal',
            can_access_admin_agent=False
        ),
        UserTier.ADMIN: UserCapabilities(
            tier=UserTier.ADMIN,
            max_repos=1000,
            max_agents=50,
            context_indexer_type='chroma',
            gpu_access=True,
            gpu_size='large',
            advanced_features=['all_features', 'system_admin', 'user_management'],
            rate_limit_per_hour=1000,
            support_level='admin',
            can_access_admin_agent=False  # Admin cannot access Admin Agent
        ),
        UserTier.DEVELOPER: UserCapabilities(
            tier=UserTier.DEVELOPER,
            max_repos=10000,
            max_agents=100,
            context_indexer_type='chroma',
            gpu_access=True,
            gpu_size='large',
            advanced_features=['all_features', 'admin_agent_access', 'agent_creation', 'system_control'],
            rate_limit_per_hour=10000,
            support_level='developer',
            can_access_admin_agent=True  # Only developer can access Admin Agent
        )
    }
    
    def __init__(self, users_file: str = 'users.json'):
        self.users_file = users_file
        self.users = self._load_users()
        self.current_user = None
        
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load users file: {e}")
        return {}
    
    def _save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save users file: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _check_admin_exists(self) -> bool:
        """Check if admin user already exists"""
        return any(user.get('tier') == UserTier.ADMIN.value for user in self.users.values())
    
    def _check_developer_exists(self) -> bool:
        """Check if developer user already exists"""
        return any(user.get('tier') == UserTier.DEVELOPER.value for user in self.users.values())
    
    def create_user(self, username: str, password: str, tier: UserTier, 
                   email: str = None, created_by: str = None) -> bool:
        """Create a new user"""
        if username in self.users:
            print(f"❌ User '{username}' already exists")
            return False
        
        # Check admin uniqueness
        if tier == UserTier.ADMIN and self._check_admin_exists():
            print(f"❌ Admin user already exists. Only one admin allowed.")
            return False
        
        # Check developer uniqueness (optional - can have multiple developers)
        if tier == UserTier.DEVELOPER and self._check_developer_exists():
            print(f"⚠️ Developer user already exists. Multiple developers allowed but be cautious.")
        
        # Validate tier permissions
        if tier in [UserTier.TESTER, UserTier.ADMIN, UserTier.DEVELOPER]:
            if not self._can_create_privileged_user(created_by):
                print(f"❌ Insufficient permissions to create {tier.value} user")
                return False
        
        user_data = {
            'username': username,
            'password_hash': self._hash_password(password),
            'tier': tier.value,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'created_by': created_by,
            'last_login': None,
            'status': 'active',  # active, blocked, deleted
            'usage_stats': {
                'repos_created': 0,
                'agents_used': 0,
                'requests_this_hour': 0,
                'last_request_time': None
            }
        }
        
        self.users[username] = user_data
        self._save_users()
        print(f"✅ Created {tier.value} user: {username}")
        return True
    
    def _can_create_privileged_user(self, created_by: str) -> bool:
        """Check if user can create privileged accounts"""
        if not created_by:
            return False
        
        creator = self.users.get(created_by)
        if not creator:
            return False
        
        creator_tier = UserTier(creator['tier'])
        # Only admin or developer can create privileged users
        return creator_tier in [UserTier.ADMIN, UserTier.DEVELOPER]
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user"""
        user = self.users.get(username)
        if not user:
            print(f"❌ User '{username}' not found")
            return False
        
        # Check if user is blocked or deleted
        if user.get('status') != 'active':
            print(f"❌ User '{username}' is {user.get('status', 'inactive')}")
            return False
        
        if user['password_hash'] != self._hash_password(password):
            print(f"❌ Invalid password for user '{username}'")
            return False
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self._save_users()
        
        self.current_user = username
        print(f"✅ Authenticated as {username} ({user['tier']})")
        return True
    
    def get_current_user_capabilities(self) -> Optional[UserCapabilities]:
        """Get capabilities for current user"""
        if not self.current_user:
            return None
        
        user = self.users.get(self.current_user)
        if not user:
            return None
        
        tier = UserTier(user['tier'])
        return self.TIER_CAPABILITIES[tier]
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if current user can access a specific feature"""
        capabilities = self.get_current_user_capabilities()
        if not capabilities:
            return False
        
        return feature in capabilities.advanced_features
    
    def can_access_admin_agent(self) -> bool:
        """Check if current user can access Admin Agent"""
        capabilities = self.get_current_user_capabilities()
        return capabilities.can_access_admin_agent if capabilities else False
    
    def can_use_context_indexer(self, indexer_type: str) -> bool:
        """Check if user can use specific context indexer type"""
        capabilities = self.get_current_user_capabilities()
        if not capabilities:
            return False
        
        # Free users can only use simple indexer
        if capabilities.tier == UserTier.FREE:
            return indexer_type == 'simple'
        
        # Advanced users can use FAISS
        if capabilities.tier == UserTier.ADVANCED:
            return indexer_type in ['simple', 'faiss']
        
        # Premium/Admin/Tester/Developer can use all indexers
        return indexer_type in ['simple', 'faiss', 'chroma']
    
    def can_access_gpu(self) -> bool:
        """Check if user can access GPU resources"""
        capabilities = self.get_current_user_capabilities()
        return capabilities.gpu_access if capabilities else False
    
    def get_gpu_size(self) -> str:
        """Get GPU size for current user"""
        capabilities = self.get_current_user_capabilities()
        return capabilities.gpu_size if capabilities else 'none'
    
    def check_rate_limit(self) -> bool:
        """Check if user has exceeded rate limit"""
        if not self.current_user:
            return False
        
        user = self.users.get(self.current_user)
        if not user:
            return False
        
        capabilities = self.get_current_user_capabilities()
        if not capabilities:
            return False
        
        now = datetime.now()
        last_request = user['usage_stats'].get('last_request_time')
        
        # Reset hourly counter if needed
        if last_request:
            last_request_time = datetime.fromisoformat(last_request)
            if now - last_request_time > timedelta(hours=1):
                user['usage_stats']['requests_this_hour'] = 0
        
        # Check rate limit
        current_requests = user['usage_stats'].get('requests_this_hour', 0)
        if current_requests >= capabilities.rate_limit_per_hour:
            print(f"⚠️ Rate limit exceeded for {self.current_user}")
            return False
        
        # Update usage
        user['usage_stats']['requests_this_hour'] = current_requests + 1
        user['usage_stats']['last_request_time'] = now.isoformat()
        self._save_users()
        
        return True
    
    def increment_usage(self, usage_type: str):
        """Increment usage statistics"""
        if not self.current_user:
            return
        
        user = self.users.get(self.current_user)
        if not user:
            return
        
        if usage_type == 'repo':
            user['usage_stats']['repos_created'] += 1
        elif usage_type == 'agent':
            user['usage_stats']['agents_used'] += 1
        
        self._save_users()
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary for current user"""
        if not self.current_user:
            return {}
        
        user = self.users.get(self.current_user)
        if not user:
            return {}
        
        capabilities = self.get_current_user_capabilities()
        
        return {
            'username': self.current_user,
            'tier': user['tier'],
            'status': user.get('status', 'active'),
            'capabilities': {
                'max_repos': capabilities.max_repos,
                'max_agents': capabilities.max_agents,
                'context_indexer_type': capabilities.context_indexer_type,
                'gpu_access': capabilities.gpu_access,
                'gpu_size': capabilities.gpu_size,
                'rate_limit_per_hour': capabilities.rate_limit_per_hour,
                'can_access_admin_agent': capabilities.can_access_admin_agent
            },
            'usage': user['usage_stats'],
            'support_level': capabilities.support_level
        }
    
    def upgrade_user(self, username: str, new_tier: UserTier, upgraded_by: str = None) -> bool:
        """Upgrade user tier (admin only)"""
        if not self._can_create_privileged_user(upgraded_by):
            print("❌ Insufficient permissions to upgrade user")
            return False
        
        if username not in self.users:
            print(f"❌ User '{username}' not found")
            return False
        
        # Check admin uniqueness
        if new_tier == UserTier.ADMIN and self._check_admin_exists():
            existing_admin = next((u for u in self.users.values() if u.get('tier') == UserTier.ADMIN.value), None)
            if existing_admin and existing_admin['username'] != username:
                print(f"❌ Admin user already exists: {existing_admin['username']}")
                return False
        
        old_tier = self.users[username]['tier']
        self.users[username]['tier'] = new_tier.value
        self.users[username]['upgraded_at'] = datetime.now().isoformat()
        self.users[username]['upgraded_by'] = upgraded_by
        
        self._save_users()
        print(f"✅ Upgraded {username} from {old_tier} to {new_tier.value}")
        return True
    
    def block_user(self, username: str, blocked_by: str = None) -> bool:
        """Block a user (admin only)"""
        if not self._can_create_privileged_user(blocked_by):
            print("❌ Insufficient permissions to block user")
            return False
        
        if username not in self.users:
            print(f"❌ User '{username}' not found")
            return False
        
        # Admin cannot block themselves
        if username == blocked_by:
            print("❌ Admin cannot block themselves")
            return False
        
        self.users[username]['status'] = 'blocked'
        self.users[username]['blocked_at'] = datetime.now().isoformat()
        self.users[username]['blocked_by'] = blocked_by
        
        self._save_users()
        print(f"✅ Blocked user: {username}")
        return True
    
    def unblock_user(self, username: str, unblocked_by: str = None) -> bool:
        """Unblock a user (admin only)"""
        if not self._can_create_privileged_user(unblocked_by):
            print("❌ Insufficient permissions to unblock user")
            return False
        
        if username not in self.users:
            print(f"❌ User '{username}' not found")
            return False
        
        self.users[username]['status'] = 'active'
        self.users[username]['unblocked_at'] = datetime.now().isoformat()
        self.users[username]['unblocked_by'] = unblocked_by
        
        self._save_users()
        print(f"✅ Unblocked user: {username}")
        return True
    
    def delete_user(self, username: str, deleted_by: str = None) -> bool:
        """Delete a user (admin only)"""
        if not self._can_create_privileged_user(deleted_by):
            print("❌ Insufficient permissions to delete user")
            return False
        
        if username not in self.users:
            print(f"❌ User '{username}' not found")
            return False
        
        # Admin cannot delete themselves
        if username == deleted_by:
            print("❌ Admin cannot delete themselves")
            return False
        
        # Soft delete - mark as deleted but keep record
        self.users[username]['status'] = 'deleted'
        self.users[username]['deleted_at'] = datetime.now().isoformat()
        self.users[username]['deleted_by'] = deleted_by
        
        self._save_users()
        print(f"✅ Deleted user: {username}")
        return True
    
    def list_users(self, admin_user: str = None) -> List[Dict[str, Any]]:
        """List all users (admin only)"""
        if admin_user and not self._can_create_privileged_user(admin_user):
            print("❌ Insufficient permissions to list users")
            return []
        
        return [
            {
                'username': username,
                'tier': user['tier'],
                'status': user.get('status', 'active'),
                'email': user.get('email'),
                'created_at': user['created_at'],
                'last_login': user.get('last_login'),
                'usage_stats': user['usage_stats']
            }
            for username, user in self.users.items()
        ]

# Global user manager instance
user_manager = UserManager()

def get_user_manager() -> UserManager:
    """Get the global user manager instance"""
    return user_manager 