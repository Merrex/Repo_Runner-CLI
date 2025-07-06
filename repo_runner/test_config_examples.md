# 🧪 Testing Configuration Guide

## Setting Free Models for Testing

### **Option 1: Environment Variables (Recommended)**

```bash
# Set all agents to use free models
export DETECTION_AGENT_MODEL_TYPE='default'
export REQUIREMENTS_AGENT_MODEL_TYPE='default'
export SETUP_AGENT_MODEL_TYPE='default'
export FIXER_AGENT_MODEL_TYPE='default'
export DB_AGENT_MODEL_TYPE='default'
export HEALTH_AGENT_MODEL_TYPE='default'
export RUNNER_AGENT_MODEL_TYPE='default'

# Or set specific free models
export DETECTION_MODEL='microsoft/DialoGPT-small'
export REQUIREMENTS_MODEL='microsoft/DialoGPT-medium'
export SETUP_MODEL='microsoft/DialoGPT-medium'
export FIXER_MODEL='microsoft/DialoGPT-medium'
export DB_MODEL='microsoft/DialoGPT-medium'
export HEALTH_MODEL='microsoft/DialoGPT-small'
export RUNNER_MODEL='microsoft/DialoGPT-medium'
```

### **Option 2: .env File**

Create a `.env` file in your project root:

```env
# Testing Configuration - Free Models Only
DETECTION_AGENT_MODEL_TYPE=default
REQUIREMENTS_AGENT_MODEL_TYPE=default
SETUP_AGENT_MODEL_TYPE=default
FIXER_AGENT_MODEL_TYPE=default
DB_AGENT_MODEL_TYPE=default
HEALTH_AGENT_MODEL_TYPE=default
RUNNER_AGENT_MODEL_TYPE=default

# Or specify exact free models
DETECTION_MODEL=microsoft/DialoGPT-small
REQUIREMENTS_MODEL=microsoft/DialoGPT-medium
SETUP_MODEL=microsoft/DialoGPT-medium
FIXER_MODEL=microsoft/DialoGPT-medium
DB_MODEL=microsoft/DialoGPT-medium
HEALTH_MODEL=microsoft/DialoGPT-small
RUNNER_MODEL=microsoft/DialoGPT-medium
```

### **Option 3: System-Wide Configuration**

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Add these lines to your shell profile
export DETECTION_AGENT_MODEL_TYPE='default'
export REQUIREMENTS_AGENT_MODEL_TYPE='default'
export SETUP_AGENT_MODEL_TYPE='default'
export FIXER_AGENT_MODEL_TYPE='default'
export DB_AGENT_MODEL_TYPE='default'
export HEALTH_AGENT_MODEL_TYPE='default'
export RUNNER_AGENT_MODEL_TYPE='default'
```

### **Option 4: Minimal Testing Configuration**

For the fastest testing with smallest models:

```bash
# Use smallest models for fastest testing
export DETECTION_MODEL='microsoft/DialoGPT-small'
export REQUIREMENTS_MODEL='microsoft/DialoGPT-small'
export SETUP_MODEL='microsoft/DialoGPT-small'
export FIXER_MODEL='microsoft/DialoGPT-small'
export DB_MODEL='microsoft/DialoGPT-small'
export HEALTH_MODEL='microsoft/DialoGPT-small'
export RUNNER_MODEL='microsoft/DialoGPT-small'
```

## 🚀 **Quick Testing Setup**

### **Step 1: Set Free Models**
```bash
# Set all agents to use free models
export DETECTION_AGENT_MODEL_TYPE='default'
export REQUIREMENTS_AGENT_MODEL_TYPE='default'
export SETUP_AGENT_MODEL_TYPE='default'
export FIXER_AGENT_MODEL_TYPE='default'
export DB_AGENT_MODEL_TYPE='default'
export HEALTH_AGENT_MODEL_TYPE='default'
export RUNNER_AGENT_MODEL_TYPE='default'
```

### **Step 2: Install and Test**
```bash
# Install the tool
pip install git+https://github.com/Merrex/Repo_Runner-CLI.git

# Auto-install dependencies
repo_runner install

# Test models
repo_runner test_models

# Run on your repository
repo_runner run /path/to/your/repo
```

## 📊 **Model Performance for Testing**

| Model | Parameters | Memory (GB) | Speed | Best For |
|-------|------------|-------------|-------|----------|
| DialoGPT-small | 117M | 0.5 | Fastest | Quick testing |
| DialoGPT-medium | 345M | 1.5 | Fast | Balanced testing |
| DialoGPT-large | 774M | 3.0 | Moderate | Quality testing |

## 🔧 **Verification Commands**

### **Check Current Configuration**
```bash
# List all available models and current settings
repo_runner models
```

### **Test Model Loading**
```bash
# Test that all models load correctly
repo_runner test_models
```

### **Check Environment Variables**
```bash
# Check if environment variables are set
env | grep -i "agent_model_type"
env | grep -i "_model="
```

## 💡 **Testing Best Practices**

1. **Start with small models** for fastest iteration
2. **Use consistent model types** across all agents
3. **Test in isolated environment** to avoid conflicts
4. **Monitor memory usage** during testing
5. **Use verbose logging** for debugging

## 🐛 **Troubleshooting**

### **If models still try to use gated/paid models:**
```bash
# Force all agents to use default (free) models
export DETECTION_AGENT_MODEL_TYPE='default'
export REQUIREMENTS_AGENT_MODEL_TYPE='default'
export SETUP_AGENT_MODEL_TYPE='default'
export FIXER_AGENT_MODEL_TYPE='default'
export DB_AGENT_MODEL_TYPE='default'
export HEALTH_AGENT_MODEL_TYPE='default'
export RUNNER_AGENT_MODEL_TYPE='default'

# Clear any specific model overrides
unset DETECTION_MODEL
unset REQUIREMENTS_MODEL
unset SETUP_MODEL
unset FIXER_MODEL
unset DB_MODEL
unset HEALTH_MODEL
unset RUNNER_MODEL
```

### **If you get authentication errors:**
```bash
# Clear any tokens/keys that might interfere
unset DETECTION_TOKEN
unset REQUIREMENTS_TOKEN
unset SETUP_TOKEN
unset FIXER_TOKEN
unset DB_TOKEN
unset HEALTH_TOKEN
unset RUNNER_TOKEN
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset GOOGLE_API_KEY
```

## 🎯 **Quick Test Script**

Create a test script `test_free_models.sh`:

```bash
#!/bin/bash

echo "🧪 Setting up free models for testing..."

# Set all agents to use free models
export DETECTION_AGENT_MODEL_TYPE='default'
export REQUIREMENTS_AGENT_MODEL_TYPE='default'
export SETUP_AGENT_MODEL_TYPE='default'
export FIXER_AGENT_MODEL_TYPE='default'
export DB_AGENT_MODEL_TYPE='default'
export HEALTH_AGENT_MODEL_TYPE='default'
export RUNNER_AGENT_MODEL_TYPE='default'

echo "✅ Free models configured!"
echo "🔧 Running tests..."

# Test models
repo_runner test_models

echo "🎉 Testing completed!"
```

Make it executable and run:
```bash
chmod +x test_free_models.sh
./test_free_models.sh
``` 