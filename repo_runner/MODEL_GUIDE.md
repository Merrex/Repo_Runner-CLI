# 🤖 Universal Model Configuration Guide

## Overview

This guide explains how to configure LLM models for the repo_runner tool, supporting **public**, **gated**, and **paid** models with proper authentication and fallback mechanisms.

## 🌐 Universal Model Support

The tool now supports **three types of models** with automatic authentication and fallback:

### 1. 🆓 Public Models (Default)

**Free, open-source models** that don't require any authentication:

| Agent | Model | Parameters | Use Case |
|-------|-------|------------|----------|
| DetectionAgent | microsoft/DialoGPT-medium | 345M | Repository analysis |
| RequirementsAgent | microsoft/DialoGPT-medium | 345M | Dependency analysis |
| SetupAgent | microsoft/DialoGPT-medium | 345M | Environment setup |
| FixerAgent | microsoft/DialoGPT-medium | 345M | Issue resolution |
| DBAgent | microsoft/DialoGPT-medium | 345M | Database configuration |
| HealthAgent | microsoft/DialoGPT-small | 117M | Health monitoring |
| RunnerAgent | microsoft/DialoGPT-medium | 345M | Service startup |

### 2. 🔒 Gated Models (Free Token)

**Advanced models** that require a free Hugging Face token:

| Agent | Model | Parameters | Authentication |
|-------|-------|------------|----------------|
| DetectionAgent | mistralai/Mistral-7B-Instruct-v0.2 | 7B | HF Token |
| RequirementsAgent | mistralai/Mistral-7B-Instruct-v0.2 | 7B | HF Token |
| SetupAgent | mistralai/Mistral-7B-Instruct-v0.2 | 7B | HF Token |
| FixerAgent | WizardLM/WizardCoder-1B-V1.0 | 1B | HF Token |
| DBAgent | mistralai/Mistral-7B-Instruct-v0.2 | 7B | HF Token |
| HealthAgent | HuggingFaceH4/zephyr-1.3b | 1.3B | HF Token |
| RunnerAgent | mistralai/Mistral-7B-Instruct-v0.2 | 7B | HF Token |

### 3. 💰 Paid Models (API Key)

**Premium models** that require paid API keys:

| Agent | Model | Provider | Authentication |
|-------|-------|----------|----------------|
| DetectionAgent | gpt-3.5-turbo | OpenAI | API Key |
| RequirementsAgent | gpt-4 | OpenAI | API Key |
| SetupAgent | gpt-4 | OpenAI | API Key |
| FixerAgent | gpt-4 | OpenAI | API Key |
| DBAgent | gpt-4 | OpenAI | API Key |
| HealthAgent | gpt-3.5-turbo | OpenAI | API Key |
| RunnerAgent | gpt-4 | OpenAI | API Key |

### ✅ Universal Benefits

- **Automatic fallback** to public models if authentication fails
- **Multiple provider support** (OpenAI, Anthropic, Google)
- **Environment-based configuration** for easy switching
- **Graceful error handling** with helpful error messages
- **Cost optimization** with smart model selection

## 🔑 Advanced Models (Optional)

For users who want more powerful models, you can use advanced models with Hugging Face tokens:

### Getting a Hugging Face Token

1. **Create a free account**: https://huggingface.co/join
2. **Get your token**: https://huggingface.co/settings/tokens
3. **Set environment variables**:

```bash
# Set tokens for each agent
export DETECTION_TOKEN='hf_your_token_here'
export REQUIREMENTS_TOKEN='hf_your_token_here'
export SETUP_TOKEN='hf_your_token_here'
export FIXER_TOKEN='hf_your_token_here'
export DB_TOKEN='hf_your_token_here'
export HEALTH_TOKEN='hf_your_token_here'
export RUNNER_TOKEN='hf_your_token_here'
```

### Advanced Model Options

| Agent | Free Model | Advanced Model | Parameters |
|-------|------------|----------------|------------|
| DetectionAgent | DialoGPT-medium | DialoGPT-large | 774M |
| RequirementsAgent | DialoGPT-medium | DialoGPT-large | 774M |
| SetupAgent | DialoGPT-medium | DialoGPT-large | 774M |
| FixerAgent | DialoGPT-medium | DialoGPT-large | 774M |
| DBAgent | DialoGPT-medium | DialoGPT-large | 774M |
| HealthAgent | DialoGPT-small | DialoGPT-medium | 345M |
| RunnerAgent | DialoGPT-medium | DialoGPT-large | 774M |

## 🚀 Quick Start

### 1. Install the Tool

```bash
pip install git+https://github.com/Merrex/Repo_Runner-CLI.git
```

### 2. Auto-Install Dependencies

```bash
repo_runner install
```

### 3. List Available Models

```bash
repo_runner models
```

### 4. Test Models (Optional)

```bash
repo_runner test_models
```

### 5. Run on Your Repository

```bash
repo_runner run /path/to/your/repo
```

## ⚙️ Configuration Options

### Environment Variables

You can customize models using environment variables:

```bash
# Use specific models
export DETECTION_MODEL='microsoft/DialoGPT-large'
export REQUIREMENTS_MODEL='microsoft/DialoGPT-large'
export SETUP_MODEL='microsoft/DialoGPT-large'

# Set tokens for advanced models
export DETECTION_TOKEN='hf_your_token_here'
export REQUIREMENTS_TOKEN='hf_your_token_here'
```

### .env File

Create a `.env` file in your project:

```env
# Model Configuration
DETECTION_MODEL=microsoft/DialoGPT-large
REQUIREMENTS_MODEL=microsoft/DialoGPT-large
SETUP_MODEL=microsoft/DialoGPT-large
FIXER_MODEL=microsoft/DialoGPT-large
DB_MODEL=microsoft/DialoGPT-large
HEALTH_MODEL=microsoft/DialoGPT-medium
RUNNER_MODEL=microsoft/DialoGPT-large

# Token Configuration (Optional)
DETECTION_TOKEN=hf_your_token_here
REQUIREMENTS_TOKEN=hf_your_token_here
SETUP_TOKEN=hf_your_token_here
FIXER_TOKEN=hf_your_token_here
DB_TOKEN=hf_your_token_here
HEALTH_TOKEN=hf_your_token_here
RUNNER_TOKEN=hf_your_token_here
```

## 📊 Model Performance Comparison

| Model | Parameters | Memory (GB) | Speed (req/s) | Accuracy | Cost |
|-------|------------|-------------|---------------|----------|------|
| DialoGPT-small | 117M | 0.5 | 10-20 | Good | Free |
| DialoGPT-medium | 345M | 1.5 | 5-10 | Very Good | Free |
| DialoGPT-large | 774M | 3.0 | 2-5 | Excellent | Free |

## 🔧 Troubleshooting

### Common Issues

1. **"Failed to load model"**
   ```bash
   # Check if model exists
   repo_runner test_models
   
   # Use fallback models
   export DETECTION_MODEL='microsoft/DialoGPT-small'
   ```

2. **"Gated repo" errors**
   ```bash
   # Use free models instead
   export DETECTION_MODEL='microsoft/DialoGPT-medium'
   export REQUIREMENTS_MODEL='microsoft/DialoGPT-medium'
   ```

3. **"Out of memory" errors**
   ```bash
   # Use smaller models
   export DETECTION_MODEL='microsoft/DialoGPT-small'
   export HEALTH_MODEL='microsoft/DialoGPT-small'
   ```

4. **"Authentication required"**
   ```bash
   # Get free token from Hugging Face
   # https://huggingface.co/settings/tokens
   export DETECTION_TOKEN='hf_your_token_here'
   ```

### Solutions

1. **Memory Issues**: Use DialoGPT-small models
2. **Speed Issues**: Reduce max_tokens in configuration
3. **Authentication Issues**: Use free models or get HF token
4. **Download Issues**: Check internet connection

## 🎯 Best Practices

### For Development/Testing
- Use **DialoGPT-small** for fast iteration
- Set lower `max_tokens` for faster responses
- Use CPU-only mode if GPU memory is limited

### For Production
- Use **DialoGPT-medium** for balanced performance
- Use **DialoGPT-large** for complex reasoning
- Set appropriate `max_tokens` for detailed responses

### For Resource-Constrained Environments
- Use **DialoGPT-small** for all agents
- Reduce `max_tokens` to 256-512
- Use CPU-only mode

## 📝 Example Configurations

### Minimal Configuration (Fastest)
```bash
export DETECTION_MODEL='microsoft/DialoGPT-small'
export REQUIREMENTS_MODEL='microsoft/DialoGPT-small'
export SETUP_MODEL='microsoft/DialoGPT-small'
export FIXER_MODEL='microsoft/DialoGPT-small'
export DB_MODEL='microsoft/DialoGPT-small'
export HEALTH_MODEL='microsoft/DialoGPT-small'
export RUNNER_MODEL='microsoft/DialoGPT-small'
```

### Balanced Configuration (Recommended)
```bash
export DETECTION_MODEL='microsoft/DialoGPT-medium'
export REQUIREMENTS_MODEL='microsoft/DialoGPT-medium'
export SETUP_MODEL='microsoft/DialoGPT-medium'
export FIXER_MODEL='microsoft/DialoGPT-medium'
export DB_MODEL='microsoft/DialoGPT-medium'
export HEALTH_MODEL='microsoft/DialoGPT-small'
export RUNNER_MODEL='microsoft/DialoGPT-medium'
```

### Maximum Performance Configuration
```bash
export DETECTION_MODEL='microsoft/DialoGPT-large'
export REQUIREMENTS_MODEL='microsoft/DialoGPT-large'
export SETUP_MODEL='microsoft/DialoGPT-large'
export FIXER_MODEL='microsoft/DialoGPT-large'
export DB_MODEL='microsoft/DialoGPT-large'
export HEALTH_MODEL='microsoft/DialoGPT-medium'
export RUNNER_MODEL='microsoft/DialoGPT-large'
```

## 🆘 Getting Help

### Commands to Check Status

```bash
# Check model configuration
repo_runner models

# Test all models
repo_runner test_models

# Check installation
repo_runner install
```

### Debug Mode

```bash
# Run with verbose logging
repo_runner run /path/to/repo --verbose
```

## 📚 Additional Resources

- [Hugging Face Models](https://huggingface.co/models)
- [DialoGPT Documentation](https://huggingface.co/microsoft/DialoGPT-medium)
- [Transformers Library](https://huggingface.co/docs/transformers)
- [Token Management](https://huggingface.co/settings/tokens)

---

**💡 Pro Tip**: Start with free models for testing, then upgrade to advanced models for production use! 