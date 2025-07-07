# 🔧 Universal Configuration Guide

## Overview

This guide explains how to configure **all tokens, API keys, and settings** for the repo_runner tool in one centralized location.

## 🚀 Quick Setup

### 1. Create Configuration Template

```bash
# Generate .env template with all possible settings
repo_runner config
```

### 2. Edit Your Configuration

```bash
# Edit the template with your actual tokens
nano .env.template

# Rename to .env
mv .env.template .env
```

### 3. Check Configuration Status

```bash
# Verify your configuration
repo_runner status
```

## 📋 Configuration Categories

### 🤖 LLM Model Configuration

**Free Models (Default)**
```env
# All agents use free models by default
DETECTION_AGENT_MODEL_TYPE=default
REQUIREMENTS_AGENT_MODEL_TYPE=default
SETUP_AGENT_MODEL_TYPE=default
FIXER_AGENT_MODEL_TYPE=default
DB_AGENT_MODEL_TYPE=default
HEALTH_AGENT_MODEL_TYPE=default
RUNNER_AGENT_MODEL_TYPE=default
```

**Advanced Models (Free Token Required)**
```env
# Use gated models with Hugging Face token
DETECTION_AGENT_MODEL_TYPE=gated
DETECTION_MODEL=mistralai/Mistral-7B-Instruct-v0.2
DETECTION_TOKEN=hf_your_token_here

REQUIREMENTS_AGENT_MODEL_TYPE=gated
REQUIREMENTS_MODEL=mistralai/Mistral-7B-Instruct-v0.2
REQUIREMENTS_TOKEN=hf_your_token_here
```

**Premium Models (Paid API Required)**
```env
# Use OpenAI models with API key
DETECTION_AGENT_MODEL_TYPE=premium
DETECTION_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-your_key_here

REQUIREMENTS_AGENT_MODEL_TYPE=premium
REQUIREMENTS_MODEL=gpt-4
```

### 🔑 API Keys

**OpenAI**
```env
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_ORG_ID=org-your_org_id_here
```

**Anthropic**
```env
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

**Google**
```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_PROJECT_ID=your_project_id_here
```

**Hugging Face**
```env
HF_TOKEN=hf_your_token_here
```

### 🔌 Third Party Integrations

**Ngrok (Required for Colab/Cloud)**
```env
# Get free token: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN=your_ngrok_token_here
NGROK_REGION=us
NGROK_DOMAIN=your_custom_domain.ngrok.io
```

**Cloudflare**
```env
CLOUDFLARE_API_TOKEN=your_cloudflare_token_here
CLOUDFLARE_ZONE_ID=your_zone_id_here
```

**Docker Hub**
```env
DOCKERHUB_USERNAME=your_username
DOCKERHUB_PASSWORD=your_password
DOCKERHUB_TOKEN=your_token_here
```

**Cloud Providers**
```env
# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Google Cloud
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_SERVICE_ACCOUNT_KEY=your_service_account_key

# Azure
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
```

### 🌍 Environment Settings

```env
# Execution mode
REPO_RUNNER_MODE=local  # or 'cloud'

# Debug and logging
REPO_RUNNER_DEBUG=false
REPO_RUNNER_LOG_LEVEL=INFO

# Performance
REPO_RUNNER_TIMEOUT=300
REPO_RUNNER_MAX_WORKERS=4
```

### 🔌 Port Management

```env
# Port configuration
DEFAULT_START_PORT=3000
PORT_RANGE=100
ENABLE_NGROK=true
ENABLE_CLOUDFLARE=false
HEALTH_CHECK_TIMEOUT=30
```

## 🎯 Common Use Cases

### 1. **Local Development (Minimal Setup)**

```env
# Just the basics - everything else uses defaults
REPO_RUNNER_MODE=local
REPO_RUNNER_DEBUG=true
```

### 2. **Colab/Cloud Environment**

```env
# Required for cloud environments
NGROK_AUTH_TOKEN=your_ngrok_token_here
REPO_RUNNER_MODE=cloud

# Optional: Use better models
DETECTION_AGENT_MODEL_TYPE=gated
DETECTION_TOKEN=hf_your_token_here
```

### 3. **Production with Premium Models**

```env
# Use OpenAI for best performance
DETECTION_AGENT_MODEL_TYPE=premium
REQUIREMENTS_AGENT_MODEL_TYPE=premium
SETUP_AGENT_MODEL_TYPE=premium
OPENAI_API_KEY=sk-your_key_here

# Production settings
REPO_RUNNER_MODE=local
REPO_RUNNER_DEBUG=false
REPO_RUNNER_TIMEOUT=600
```

### 4. **Advanced Development**

```env
# Use gated models for better performance
DETECTION_AGENT_MODEL_TYPE=gated
REQUIREMENTS_AGENT_MODEL_TYPE=gated
SETUP_AGENT_MODEL_TYPE=gated
HF_TOKEN=hf_your_token_here

# Ngrok for external access
NGROK_AUTH_TOKEN=your_ngrok_token_here

# Debug mode
REPO_RUNNER_DEBUG=true
REPO_RUNNER_LOG_LEVEL=DEBUG
```

## 🔧 Getting Tokens

### **Ngrok Token (Free)**
1. Go to: https://dashboard.ngrok.com/signup
2. Create free account
3. Get token: https://dashboard.ngrok.com/get-started/your-authtoken
4. Add to `.env`: `NGROK_AUTH_TOKEN=your_token`

### **Hugging Face Token (Free)**
1. Go to: https://huggingface.co/join
2. Create free account
3. Get token: https://huggingface.co/settings/tokens
4. Add to `.env`: `HF_TOKEN=hf_your_token`

### **OpenAI API Key (Paid)**
1. Go to: https://platform.openai.com/api-keys
2. Create API key
3. Add to `.env`: `OPENAI_API_KEY=sk-your_key`

### **Anthropic API Key (Paid)**
1. Go to: https://console.anthropic.com/
2. Create API key
3. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-your_key`

## 🧪 Testing Configuration

### **Test All Models**
```bash
repo_runner test_models
```

### **Check Configuration Status**
```bash
repo_runner status
```

### **Validate Configuration**
```bash
repo_runner config
```

## 🚨 Troubleshooting

### **"Ngrok authentication failed"**
```bash
# Add your ngrok token to .env
echo "NGROK_AUTH_TOKEN=your_token_here" >> .env
```

### **"Model not available"**
```bash
# Use free models instead
export DETECTION_AGENT_MODEL_TYPE=default
export REQUIREMENTS_AGENT_MODEL_TYPE=default
```

### **"API key required"**
```bash
# Add your API key to .env
echo "OPENAI_API_KEY=sk-your_key_here" >> .env
```

### **"Token not found"**
```bash
# Get free Hugging Face token
# https://huggingface.co/settings/tokens
echo "HF_TOKEN=hf_your_token_here" >> .env
```

## 📝 Example .env File

```env
# ========================================
# repo_runner Configuration
# ========================================

# === LLM Models ===
DETECTION_AGENT_MODEL_TYPE=default
REQUIREMENTS_AGENT_MODEL_TYPE=default
SETUP_AGENT_MODEL_TYPE=default
FIXER_AGENT_MODEL_TYPE=default
DB_AGENT_MODEL_TYPE=default
HEALTH_AGENT_MODEL_TYPE=default
RUNNER_AGENT_MODEL_TYPE=default

# === API Keys ===
# OPENAI_API_KEY=sk-your_key_here
# ANTHROPIC_API_KEY=sk-ant-your_key_here
# HF_TOKEN=hf_your_token_here

# === Integrations ===
NGROK_AUTH_TOKEN=your_ngrok_token_here
NGROK_REGION=us

# === Environment ===
REPO_RUNNER_MODE=local
REPO_RUNNER_DEBUG=false
REPO_RUNNER_TIMEOUT=300

# === Ports ===
DEFAULT_START_PORT=3000
ENABLE_NGROK=true
```

## 🎯 Best Practices

### **Security**
- Never commit `.env` files to version control
- Use environment variables in production
- Rotate tokens regularly

### **Performance**
- Use `default` models for testing
- Use `gated` models for development
- Use `premium` models for production

### **Cost Optimization**
- Start with free models
- Use gated models for better performance
- Use premium models only when needed

## 📞 Support

If you encounter issues:

1. **Check configuration**: `repo_runner status`
2. **Test models**: `repo_runner test_models`
3. **Validate setup**: `repo_runner config`
4. **Check logs**: Look for error messages in output

The system will automatically fall back to free models if authentication fails, so it should always work! 