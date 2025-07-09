# Configuration Guide

## 🎯 Overview

This guide covers all configuration options for the Repo Runner system, including CLI parameters, environment variables, and tier-based feature access.

## 🚀 Quick Start

### Basic Usage
```bash
# Run with default settings (free tier)
python -m repo_runner.cli --repo_path /path/to/repo

# Run with authentication
python -m repo_runner.cli --login --username your_user --password your_pass --repo_path /path/to/repo
```

### Admin Setup (First Time)
```bash
# Register as admin (only one admin allowed)
python -m repo_runner.cli --register --username admin --password your_secure_password --tier admin

# Login as admin
python -m repo_runner.cli --login --username admin --password your_secure_password
```

## 📋 CLI Parameters

### Core Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--repo_path` | string | required | Path to the repository to analyze |
| `--env` | string | "detect" | Environment: detect, colab, aws, gcp, local |
| `--model` | string | "balanced" | Model tier: free, balanced, premium |

### Authentication Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `--login` | flag | Login with username/password |
| `--register` | flag | Register new user |
| `--username` | string | Username for authentication |
| `--password` | string | Password for authentication |
| `--tier` | string | User tier: free, advanced, premium, tester, admin |

### FAISS Configuration
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--use_faiss` | boolean | null | Force FAISS usage (Advanced/Premium only) |
| `--sentence_transformer_model` | string | "all-MiniLM-L6-v2" | Sentence transformer model |

### Workflow Control
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--skip_agents` | list | [] | Agents to skip (comma-separated) |
| `--log_level` | string | "INFO" | Logging level |

### Admin Commands
| Parameter | Type | Description |
|-----------|------|-------------|
| `--list_users` | flag | List all users (Admin only) |
| `--upgrade_user` | string | Username to upgrade (Admin only) |
| `--new_tier` | string | New tier for user upgrade (Admin only) |
| `--block_user` | string | Username to block (Admin only) |
| `--unblock_user` | string | Username to unblock (Admin only) |
| `--delete_user` | string | Username to delete (Admin only) |
| `--usage` | flag | Show usage statistics |

## 👥 User Tiers & Capabilities

### Tier Comparison
| Feature | Free | Advanced | Premium | Tester | Admin |
|---------|------|----------|---------|--------|-------|
| **Context Indexer** | Simple Text | FAISS | Chroma | FAISS | Chroma |
| **GPU Access** | ❌ | Small | Large | Medium | Large |
| **Rate Limit** | 10/hour | 50/hour | 200/hour | 100/hour | 1000/hour |
| **Max Repos** | 3 | 10 | 100 | 50 | 1000 |
| **Support** | Community | Email | Priority | Internal | Admin |
| **User Management** | ❌ | ❌ | ❌ | ❌ | ✅ |

### Tier-Specific Features

#### Free Tier
- Simple text-based context search
- No GPU access
- Basic rate limiting (10 requests/hour)
- Community support
- Maximum 3 repositories

#### Advanced Tier
- FAISS context indexing (if recommended by agents)
- Small GPU access
- Moderate rate limiting (50 requests/hour)
- Email support
- Maximum 10 repositories

#### Premium Tier
- Chroma context indexing (best available)
- Large GPU access
- High rate limiting (200 requests/hour)
- Priority support
- Maximum 100 repositories

#### Tester Tier
- FAISS context indexing (always available)
- Medium GPU access
- High rate limiting (100 requests/hour)
- Internal support
- Maximum 50 repositories

#### Admin Tier
- Chroma context indexing (best available)
- Large GPU access
- Unlimited rate limiting (1000 requests/hour)
- Admin support
- Maximum 1000 repositories
- User management capabilities

## 🔧 Environment Variables

### API Keys
```bash
# OpenAI API Key
export OPENAI_API_KEY=your_openai_api_key

# Anthropic API Key
export ANTHROPIC_API_KEY=your_anthropic_api_key
```

### GPU Configuration
```bash
# CUDA Device Selection (for Premium/Admin tiers)
export CUDA_VISIBLE_DEVICES=0

# GPU Memory Configuration
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

### System Configuration
```bash
# Logging Level
export LOG_LEVEL=INFO

# Checkpoint Directory
export CHECKPOINT_DIR=./checkpoints

# User Database Path
export USER_DB_PATH=./users.json
```

## 📁 Configuration Files

### User Configuration (users.json)
```json
{
  "users": {
    "admin": {
      "password_hash": "sha256_hash_of_password",
      "tier": "admin",
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-01T12:00:00Z",
      "requests_count": 0,
      "repos_created": 0,
      "is_blocked": false
    }
  },
  "admin_exists": true
}
```

### Run State Configuration (run_state.json)
```json
{
  "repo_path": "/path/to/repo",
  "environment": "colab",
  "model_tier": "premium",
  "faiss_config": {
    "use_faiss": true,
    "sentence_transformer_model": "all-MiniLM-L6-v2"
  },
  "skip_agents": [],
  "current_phase": "setup",
  "start_time": "2024-01-01T00:00:00Z",
  "user": "premium_user"
}
```

### Agent State Configuration (agent_state_*.json)
```json
{
  "agent_name": "EnvDetectorAgent",
  "status": "completed",
  "result": {
    "environment": "colab",
    "capabilities": ["gpu", "faiss"],
    "faiss_recommendation": true
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🎛️ Advanced Configuration

### FAISS Configuration
```python
# Force FAISS usage (Advanced/Premium only)
faiss_config = {
    "use_faiss": True,  # or False, or None for agent recommendation
    "sentence_transformer_model": "all-MiniLM-L6-v2",
    "index_type": "flat",  # or "ivf", "hnsw"
    "dimension": 384
}
```

### Agent Configuration
```python
# Skip specific agents
skip_agents = ["HealthAgent", "FixerAgent"]

# Agent-specific configuration
agent_config = {
    "EnvDetectorAgent": {
        "detection_timeout": 30,
        "environment_checks": ["colab", "aws", "gcp", "local"]
    },
    "DependencyAgent": {
        "package_manager": "pip",
        "update_existing": True
    }
}
```

### Rate Limiting Configuration
```python
# Tier-based rate limits
rate_limits = {
    "free": {"requests_per_hour": 10, "repos_limit": 3},
    "advanced": {"requests_per_hour": 50, "repos_limit": 10},
    "premium": {"requests_per_hour": 200, "repos_limit": 100},
    "tester": {"requests_per_hour": 100, "repos_limit": 50},
    "admin": {"requests_per_hour": 1000, "repos_limit": 1000}
}
```

## 🔐 Security Configuration

### Password Security
```python
# Password hashing configuration
import hashlib
import os

def hash_password(password):
    salt = os.urandom(32)
    hash_obj = hashlib.sha256()
    hash_obj.update(salt + password.encode())
    return salt.hex() + hash_obj.hexdigest()

def verify_password(password, hashed):
    salt = bytes.fromhex(hashed[:64])
    hash_obj = hashlib.sha256()
    hash_obj.update(salt + password.encode())
    return hashed[64:] == hash_obj.hexdigest()
```

### Access Control
```python
# Tier-based feature access
def check_feature_access(user_tier, feature):
    access_matrix = {
        "simple_search": ["free", "advanced", "premium", "tester", "admin"],
        "faiss_search": ["advanced", "premium", "tester", "admin"],
        "chroma_search": ["premium", "admin"],
        "gpu_access": ["advanced", "premium", "tester", "admin"],
        "user_management": ["admin"]
    }
    return user_tier in access_matrix.get(feature, [])
```

## 📊 Monitoring Configuration

### Usage Tracking
```python
# Usage metrics configuration
usage_config = {
    "track_requests": True,
    "track_repos": True,
    "track_agents": True,
    "track_gpu_usage": True,
    "retention_days": 30
}
```

### Logging Configuration
```python
# Logging setup
import logging

logging_config = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": [
        {"type": "file", "filename": "repo_runner.log"},
        {"type": "console"}
    ]
}
```

## 🧪 Testing Configuration

### Test Environment
```bash
# Test configuration
export TEST_MODE=true
export TEST_USER_TIER=admin
export TEST_REPO_PATH=/tmp/test_repo
export TEST_SKIP_AGENTS=HealthAgent,FixerAgent
```

### Colab Testing
```python
# Colab-specific configuration
colab_config = {
    "use_gpu": True,
    "faiss_available": True,
    "memory_limit": "12GB",
    "timeout": 300
}
```

## 🔄 Environment-Specific Configuration

### Colab Environment
```python
# Colab-specific settings
if environment == "colab":
    config.update({
        "gpu_enabled": True,
        "faiss_recommended": True,
        "memory_optimized": True,
        "timeout_extended": True
    })
```

### AWS Environment
```python
# AWS-specific settings
if environment == "aws":
    config.update({
        "gpu_enabled": True,
        "faiss_recommended": True,
        "scalable": True,
        "monitoring": True
    })
```

### Local Environment
```python
# Local-specific settings
if environment == "local":
    config.update({
        "gpu_enabled": False,
        "faiss_recommended": False,
        "debug_mode": True,
        "local_development": True
    })
```

## 🚨 Troubleshooting

### Common Issues

#### Authentication Issues
```bash
# Reset admin password
python -m repo_runner.cli --reset_admin --new_password new_password

# Check user status
python -m repo_runner.cli --login --username admin --password admin_pass --list_users
```

#### FAISS Issues
```bash
# Force simple text search
python -m repo_runner.cli --repo_path /path/to/repo --use_faiss false

# Check FAISS availability
python -c "import faiss; print('FAISS available')"
```

#### GPU Issues
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Disable GPU
export CUDA_VISIBLE_DEVICES=""
```

#### Rate Limiting Issues
```bash
# Check usage
python -m repo_runner.cli --login --username your_user --password your_pass --usage

# Upgrade tier (admin only)
python -m repo_runner.cli --login --username admin --password admin_pass --upgrade_user user1 --new_tier premium
```

## 📚 Examples

### Basic Repository Analysis
```bash
# Analyze a Python repository
python -m repo_runner.cli --repo_path /path/to/python/repo --env detect --model balanced

# Analyze with specific environment
python -m repo_runner.cli --repo_path /path/to/repo --env colab --model premium
```

### Advanced Usage
```bash
# Skip specific agents
python -m repo_runner.cli --repo_path /path/to/repo --skip_agents HealthAgent,FixerAgent

# Force FAISS (Advanced/Premium only)
python -m repo_runner.cli --repo_path /path/to/repo --use_faiss true

# Custom sentence transformer model
python -m repo_runner.cli --repo_path /path/to/repo --sentence_transformer_model all-mpnet-base-v2
```

### Admin Operations
```bash
# List all users
python -m repo_runner.cli --login --username admin --password admin_pass --list_users

# Upgrade user to premium
python -m repo_runner.cli --login --username admin --password admin_pass --upgrade_user user1 --new_tier premium

# Block problematic user
python -m repo_runner.cli --login --username admin --password admin_pass --block_user problematic_user
```

---

*This configuration guide is comprehensive and covers all aspects of the Repo Runner system. For specific use cases or advanced configurations, refer to the individual component documentation.* 