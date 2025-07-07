import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Graceful fallback for dotenv import
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    print("⚠️ python-dotenv not available - attempting to install automatically...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-dotenv'])
        from dotenv import load_dotenv
        DOTENV_AVAILABLE = True
        print("✅ python-dotenv installed successfully")
    except Exception as e:
        print(f"❌ Failed to install python-dotenv automatically: {e}")
        print("⚠️ Will use environment variables only")
        DOTENV_AVAILABLE = False
        # Create a dummy function
        def load_dotenv(path=None):
            pass

class ConfigManager:
    """Universal configuration manager for all tokens, API keys, and settings"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or '.env'
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from .env file and environment variables"""
        # Load from .env file if it exists
        env_file = Path(self.config_path)
        if env_file.exists():
            load_dotenv(env_file)
        
        # Load all configuration
        self.config = {
            # === LLM Model Configuration ===
            'models': self._load_model_config(),
            
            # === API Keys ===
            'api_keys': self._load_api_keys(),
            
            # === Third Party Integrations ===
            'integrations': self._load_integrations(),
            
            # === Environment Settings ===
            'environment': self._load_environment_config(),
            
            # === Port Management ===
            'ports': self._load_port_config(),
            
            # === Security ===
            'security': self._load_security_config(),
        }
    
    def _load_model_config(self) -> Dict[str, Any]:
        """Load LLM model configuration"""
        return {
            # Model types: 'default', 'gated', 'premium'
            'detection_agent': {
                'model_type': os.getenv('DETECTION_AGENT_MODEL_TYPE', 'default'),
                'model_name': os.getenv('DETECTION_MODEL', 'microsoft/DialoGPT-medium'),
                'token': os.getenv('DETECTION_TOKEN'),
                'max_tokens': int(os.getenv('DETECTION_MAX_TOKENS', '512')),
                'temperature': float(os.getenv('DETECTION_TEMPERATURE', '0.1')),
            },
            'requirements_agent': {
                'model_type': os.getenv('REQUIREMENTS_AGENT_MODEL_TYPE', 'default'),
                'model_name': os.getenv('REQUIREMENTS_MODEL', 'microsoft/DialoGPT-medium'),
                'token': os.getenv('REQUIREMENTS_TOKEN'),
                'max_tokens': int(os.getenv('REQUIREMENTS_MAX_TOKENS', '1024')),
                'temperature': float(os.getenv('REQUIREMENTS_TEMPERATURE', '0.2')),
            },
            'setup_agent': {
                'model_type': os.getenv('SETUP_AGENT_MODEL_TYPE', 'default'),
                'model_name': os.getenv('SETUP_MODEL', 'microsoft/DialoGPT-medium'),
                'token': os.getenv('SETUP_TOKEN'),
                'max_tokens': int(os.getenv('SETUP_MAX_TOKENS', '1024')),
                'temperature': float(os.getenv('SETUP_TEMPERATURE', '0.2')),
            },
            'fixer_agent': {
                'model_type': os.getenv('FIXER_AGENT_MODEL_TYPE', 'default'),
                'model_name': os.getenv('FIXER_MODEL', 'microsoft/DialoGPT-medium'),
                'token': os.getenv('FIXER_TOKEN'),
                'max_tokens': int(os.getenv('FIXER_MAX_TOKENS', '768')),
                'temperature': float(os.getenv('FIXER_TEMPERATURE', '0.1')),
            },
            'db_agent': {
                'model_type': os.getenv('DB_AGENT_MODEL_TYPE', 'default'),
                'model_name': os.getenv('DB_MODEL', 'microsoft/DialoGPT-medium'),
                'token': os.getenv('DB_TOKEN'),
                'max_tokens': int(os.getenv('DB_MAX_TOKENS', '1024')),
                'temperature': float(os.getenv('DB_TEMPERATURE', '0.2')),
            },
            'health_agent': {
                'model_type': os.getenv('HEALTH_AGENT_MODEL_TYPE', 'default'),
                'model_name': os.getenv('HEALTH_MODEL', 'microsoft/DialoGPT-small'),
                'token': os.getenv('HEALTH_TOKEN'),
                'max_tokens': int(os.getenv('HEALTH_MAX_TOKENS', '512')),
                'temperature': float(os.getenv('HEALTH_TEMPERATURE', '0.1')),
            },
            'runner_agent': {
                'model_type': os.getenv('RUNNER_AGENT_MODEL_TYPE', 'default'),
                'model_name': os.getenv('RUNNER_MODEL', 'microsoft/DialoGPT-medium'),
                'token': os.getenv('RUNNER_TOKEN'),
                'max_tokens': int(os.getenv('RUNNER_MAX_TOKENS', '1024')),
                'temperature': float(os.getenv('RUNNER_TEMPERATURE', '0.2')),
            },
        }
    
    def _load_api_keys(self) -> Dict[str, Any]:
        """Load API keys for various services"""
        return {
            # OpenAI
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'organization': os.getenv('OPENAI_ORG_ID'),
            },
            # Anthropic
            'anthropic': {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
            },
            # Google
            'google': {
                'api_key': os.getenv('GOOGLE_API_KEY'),
                'project_id': os.getenv('GOOGLE_PROJECT_ID'),
            },
            # Hugging Face
            'huggingface': {
                'token': os.getenv('HF_TOKEN'),
            },
            # GitHub
            'github': {
                'token': os.getenv('GITHUB_TOKEN'),
                'username': os.getenv('GITHUB_USERNAME'),
            },
            # GitLab
            'gitlab': {
                'token': os.getenv('GITLAB_TOKEN'),
                'url': os.getenv('GITLAB_URL', 'https://gitlab.com'),
            },
        }
    
    def _load_integrations(self) -> Dict[str, Any]:
        """Load third-party integration settings"""
        return {
            # Ngrok
            'ngrok': {
                'auth_token': os.getenv('NGROK_AUTH_TOKEN'),
                'region': os.getenv('NGROK_REGION', 'us'),
                'domain': os.getenv('NGROK_DOMAIN'),
            },
            # Cloudflare
            'cloudflare': {
                'api_token': os.getenv('CLOUDFLARE_API_TOKEN'),
                'zone_id': os.getenv('CLOUDFLARE_ZONE_ID'),
            },
            # Docker Hub
            'dockerhub': {
                'username': os.getenv('DOCKERHUB_USERNAME'),
                'password': os.getenv('DOCKERHUB_PASSWORD'),
                'token': os.getenv('DOCKERHUB_TOKEN'),
            },
            # AWS
            'aws': {
                'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                'region': os.getenv('AWS_REGION', 'us-east-1'),
            },
            # Google Cloud
            'gcp': {
                'project_id': os.getenv('GOOGLE_CLOUD_PROJECT'),
                'service_account_key': os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'),
            },
            # Azure
            'azure': {
                'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
                'tenant_id': os.getenv('AZURE_TENANT_ID'),
                'client_id': os.getenv('AZURE_CLIENT_ID'),
                'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
            },
        }
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific settings"""
        return {
            'mode': os.getenv('REPO_RUNNER_MODE', 'local'),
            'debug': os.getenv('REPO_RUNNER_DEBUG', 'false').lower() == 'true',
            'timeout': int(os.getenv('REPO_RUNNER_TIMEOUT', '300')),
            'max_workers': int(os.getenv('REPO_RUNNER_MAX_WORKERS', '4')),
            'log_level': os.getenv('REPO_RUNNER_LOG_LEVEL', 'INFO'),
        }
    
    def _load_port_config(self) -> Dict[str, Any]:
        """Load port management settings"""
        return {
            'default_start_port': int(os.getenv('DEFAULT_START_PORT', '3000')),
            'port_range': int(os.getenv('PORT_RANGE', '100')),
            'enable_ngrok': os.getenv('ENABLE_NGROK', 'true').lower() == 'true',
            'enable_cloudflare': os.getenv('ENABLE_CLOUDFLARE', 'false').lower() == 'true',
            'health_check_timeout': int(os.getenv('HEALTH_CHECK_TIMEOUT', '30')),
        }
    
    def _load_security_config(self) -> Dict[str, Any]:
        """Load security settings"""
        return {
            'check_env_vars': os.getenv('CHECK_ENV_VARS', 'true').lower() == 'true',
            'warn_default_secrets': os.getenv('WARN_DEFAULT_SECRETS', 'true').lower() == 'true',
            'allowed_hosts': os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(','),
            'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
        }
    
    def get_model_config(self, agent_name: str) -> Dict[str, Any]:
        """Get model configuration for a specific agent"""
        return self.config['models'].get(agent_name, {})
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service"""
        return self.config['api_keys'].get(service, {}).get('api_key') or \
               self.config['api_keys'].get(service, {}).get('token')
    
    def get_integration_config(self, service: str) -> Dict[str, Any]:
        """Get integration configuration for a specific service"""
        return self.config['integrations'].get(service, {})
    
    def get_environment_setting(self, key: str, default: Any = None) -> Any:
        """Get environment setting"""
        return self.config['environment'].get(key, default)
    
    def get_port_setting(self, key: str, default: Any = None) -> Any:
        """Get port management setting"""
        return self.config['ports'].get(key, default)
    
    def create_env_template(self, output_path: str = '.env.template'):
        """Create a template .env file with all possible configurations"""
        template = """# ========================================
# repo_runner Universal Configuration
# ========================================

# === LLM Model Configuration ===
# Model types: 'default' (free), 'gated' (HF token), 'premium' (API key)

# Detection Agent
DETECTION_AGENT_MODEL_TYPE=default
DETECTION_MODEL=microsoft/DialoGPT-medium
DETECTION_TOKEN=
DETECTION_MAX_TOKENS=512
DETECTION_TEMPERATURE=0.1

# Requirements Agent
REQUIREMENTS_AGENT_MODEL_TYPE=default
REQUIREMENTS_MODEL=microsoft/DialoGPT-medium
REQUIREMENTS_TOKEN=
REQUIREMENTS_MAX_TOKENS=1024
REQUIREMENTS_TEMPERATURE=0.2

# Setup Agent
SETUP_AGENT_MODEL_TYPE=default
SETUP_MODEL=microsoft/DialoGPT-medium
SETUP_TOKEN=
SETUP_MAX_TOKENS=1024
SETUP_TEMPERATURE=0.2

# Fixer Agent
FIXER_AGENT_MODEL_TYPE=default
FIXER_MODEL=microsoft/DialoGPT-medium
FIXER_TOKEN=
FIXER_MAX_TOKENS=768
FIXER_TEMPERATURE=0.1

# DB Agent
DB_AGENT_MODEL_TYPE=default
DB_MODEL=microsoft/DialoGPT-medium
DB_TOKEN=
DB_MAX_TOKENS=1024
DB_TEMPERATURE=0.2

# Health Agent
HEALTH_AGENT_MODEL_TYPE=default
HEALTH_MODEL=microsoft/DialoGPT-small
HEALTH_TOKEN=
HEALTH_MAX_TOKENS=512
HEALTH_TEMPERATURE=0.1

# Runner Agent
RUNNER_AGENT_MODEL_TYPE=default
RUNNER_MODEL=microsoft/DialoGPT-medium
RUNNER_TOKEN=
RUNNER_MAX_TOKENS=1024
RUNNER_TEMPERATURE=0.2

# === API Keys ===

# OpenAI
OPENAI_API_KEY=

# Anthropic
ANTHROPIC_API_KEY=

# Google
GOOGLE_API_KEY=
GOOGLE_PROJECT_ID=

# Hugging Face
HF_TOKEN=

# GitHub
GITHUB_TOKEN=
GITHUB_USERNAME=

# GitLab
GITLAB_TOKEN=
GITLAB_URL=https://gitlab.com

# === Third Party Integrations ===

# Ngrok (for Colab/cloud environments)
NGROK_AUTH_TOKEN=
NGROK_REGION=us
NGROK_DOMAIN=

# Cloudflare
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ZONE_ID=

# Docker Hub
DOCKERHUB_USERNAME=
DOCKERHUB_PASSWORD=
DOCKERHUB_TOKEN=

# AWS
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Google Cloud
GOOGLE_CLOUD_PROJECT=
GOOGLE_SERVICE_ACCOUNT_KEY=

# Azure
AZURE_SUBSCRIPTION_ID=
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=

# === Environment Settings ===
REPO_RUNNER_MODE=local
REPO_RUNNER_DEBUG=false
REPO_RUNNER_TIMEOUT=300
REPO_RUNNER_MAX_WORKERS=4
REPO_RUNNER_LOG_LEVEL=INFO

# === Port Management ===
DEFAULT_START_PORT=3000
PORT_RANGE=100
ENABLE_NGROK=true
ENABLE_CLOUDFLARE=false
HEALTH_CHECK_TIMEOUT=30

# === Security ===
CHECK_ENV_VARS=true
WARN_DEFAULT_SECRETS=true
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=*
"""
        
        with open(output_path, 'w') as f:
            f.write(template)
        
        print(f"✅ Created configuration template: {output_path}")
        print("📝 Edit this file with your actual tokens and settings")
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return issues"""
        issues = {
            'warnings': [],
            'errors': [],
            'missing': []
        }
        
        # Check for missing required tokens
        if self.get_environment_setting('mode') == 'cloud':
            if not self.get_integration_config('ngrok').get('auth_token'):
                issues['missing'].append('NGROK_AUTH_TOKEN (required for cloud mode)')
        
        # Check for model configuration issues
        for agent_name, config in self.config['models'].items():
            if config.get('model_type') == 'gated' and not config.get('token'):
                issues['warnings'].append(f'{agent_name.upper()}_TOKEN (recommended for gated models)')
            elif config.get('model_type') == 'premium':
                provider = 'openai'  # Default
                if not self.get_api_key(provider):
                    issues['missing'].append(f'{provider.upper()}_API_KEY (required for premium models)')
        
        return issues
    
    def print_config_summary(self):
        """Print a summary of the current configuration."""
        print("🔧 Configuration Summary")
        print("=" * 50)
        
        # Model configuration
        print("\n🤖 Model Configuration:")
        for agent, config in self.config['models'].items():
            model_type = config.get('model_type', 'default')
            model_name = config.get('model_name', 'unknown')
            has_token = "✅" if config.get('token') else "❌"
            print(f"  {agent}: {model_type} ({model_name}) {has_token}")
        
        # API keys
        print("\n🔑 API Keys:")
        for service, keys in self.config['api_keys'].items():
            has_key = "✅" if any(keys.values()) else "❌"
            print(f"  {service}: {has_key}")
        
        # Integrations
        print("\n🔌 Integrations:")
        for service, config in self.config['integrations'].items():
            has_config = "✅" if any(config.values()) else "❌"
            print(f"  {service}: {has_config}")
        
        # Environment settings
        env_config = self.config['environment']
        print(f"\n🌍 Environment: {env_config.get('mode', 'unknown')}")
        print(f"🐛 Debug: {env_config.get('debug', False)}")
        print(f"⏱️ Timeout: {env_config.get('timeout', 300)}s")
        
        print("\n✅ Configuration looks good!")
        
        print("\n💡 Next Steps:")
        print("1. Edit .env.template with your tokens and settings")
        print("2. Rename to .env: mv .env.template .env")
        print("3. Run: repo_runner run /path/to/repo")

    def debug_tokens(self):
        """Debug method to print all tokens and configuration values."""
        print("🔍 DEBUG: Token and Configuration Values")
        print("=" * 60)
        
        # Environment variables
        print("\n📋 Environment Variables:")
        env_vars = [
            'DETECTION_TOKEN', 'REQUIREMENTS_TOKEN', 'SETUP_TOKEN', 'FIXER_TOKEN',
            'DB_TOKEN', 'HEALTH_TOKEN', 'RUNNER_TOKEN',
            'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY',
            'HF_TOKEN', 'GITHUB_TOKEN', 'GITLAB_TOKEN',
            'NGROK_AUTH_TOKEN', 'CLOUDFLARE_API_TOKEN'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Show first 10 chars for security
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: ❌ NOT SET")
        
        # Current config values
        print("\n🔧 Current Configuration Values:")
        print(f"  Detection Token: {self.get_model_config('detection_agent').get('token', '❌ NOT SET')}")
        print(f"  OpenAI API Key: {self.get_api_key('openai') or '❌ NOT SET'}")
        print(f"  HuggingFace Token: {self.get_api_key('huggingface') or '❌ NOT SET'}")
        print(f"  Ngrok Auth Token: {self.get_integration_config('ngrok').get('auth_token', '❌ NOT SET')}")
        
        # File existence
        print("\n📁 File Status:")
        env_file = Path(self.config_path)
        if env_file.exists():
            print(f"  .env file: ✅ EXISTS at {env_file.absolute()}")
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    print(f"  .env file lines: {len(lines)}")
                    for line in lines[:5]:  # Show first 5 lines
                        if line.strip() and not line.startswith('#'):
                            print(f"    {line}")
                    if len(lines) > 5:
                        print(f"    ... and {len(lines) - 5} more lines")
            except Exception as e:
                print(f"  .env file read error: {e}")
        else:
            print(f"  .env file: ❌ NOT FOUND at {env_file.absolute()}")
        
        # DOTENV_AVAILABLE status
        print(f"\n🔧 DOTENV_AVAILABLE: {DOTENV_AVAILABLE}")
        
        print("\n" + "=" * 60)

# Global config manager instance
config_manager = ConfigManager() 