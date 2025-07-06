# LLM Model Configuration

## Overview

This document describes the LLM model configuration for different agents in the repo_runner system. We use different models optimized for each agent's specific role.

## Local Testing Models (Smaller, Faster)

For local testing and development, we use smaller models to reduce resource requirements:

| Agent | Model | Parameters | Max Tokens | Temperature | Use Case |
|-------|-------|------------|------------|------------|----------|
| DetectionAgent | microsoft/DialoGPT-small | 117M | 512 | 0.3 | Repository analysis |
| RequirementsAgent | microsoft/DialoGPT-medium | 345M | 1024 | 0.4 | Dependency analysis |
| SetupAgent | microsoft/DialoGPT-medium | 345M | 1024 | 0.3 | Environment setup |
| DBAgent | microsoft/DialoGPT-medium | 345M | 1024 | 0.3 | Database configuration |
| RunnerAgent | microsoft/DialoGPT-medium | 345M | 1024 | 0.3 | Service startup |
| HealthAgent | microsoft/DialoGPT-small | 117M | 512 | 0.2 | Health monitoring |
| FixerAgent | microsoft/DialoGPT-medium | 345M | 1024 | 0.4 | Issue resolution |
| Orchestrator | microsoft/DialoGPT-medium | 345M | 1024 | 0.3 | Workflow coordination |

## Production Models (Recommended)

For production use, we recommend larger models for better accuracy:

| Agent | Model | Parameters | Max Tokens | Temperature | Use Case |
|-------|-------|------------|------------|------------|----------|
| DetectionAgent | microsoft/DialoGPT-medium | 345M | 1024 | 0.3 | Repository analysis |
| RequirementsAgent | microsoft/DialoGPT-large | 774M | 2048 | 0.4 | Dependency analysis |
| SetupAgent | microsoft/DialoGPT-large | 774M | 2048 | 0.3 | Environment setup |
| DBAgent | microsoft/DialoGPT-large | 774M | 2048 | 0.3 | Database configuration |
| RunnerAgent | microsoft/DialoGPT-large | 774M | 2048 | 0.3 | Service startup |
| HealthAgent | microsoft/DialoGPT-medium | 345M | 1024 | 0.2 | Health monitoring |
| FixerAgent | microsoft/DialoGPT-large | 774M | 2048 | 0.4 | Issue resolution |
| Orchestrator | microsoft/DialoGPT-large | 774M | 2048 | 0.3 | Workflow coordination |

## Model Selection Strategy

### Local Testing
- **Smaller models**: Faster inference, lower memory usage
- **DialoGPT-small**: 117M parameters for simple tasks
- **DialoGPT-medium**: 345M parameters for complex tasks
- **Lower token limits**: Prevents hanging and reduces resource usage

### Production
- **Larger models**: Better accuracy and more nuanced responses
- **DialoGPT-medium**: 345M parameters for balanced performance
- **DialoGPT-large**: 774M parameters for complex reasoning
- **Higher token limits**: More detailed responses

## Environment Variables

You can override model selection using environment variables:

```bash
# Use specific models for agents
export DETECTION_AGENT_MODEL="microsoft/DialoGPT-large"
export REQUIREMENTS_AGENT_MODEL="microsoft/DialoGPT-large"
export SETUP_AGENT_MODEL="microsoft/DialoGPT-large"
export DB_AGENT_MODEL="microsoft/DialoGPT-large"
export RUNNER_AGENT_MODEL="microsoft/DialoGPT-large"
export HEALTH_AGENT_MODEL="microsoft/DialoGPT-medium"
export FIXER_AGENT_MODEL="microsoft/DialoGPT-large"
export ORCHESTRATOR_MODEL="microsoft/DialoGPT-large"
```

## Performance Considerations

### Local Testing
- **Memory Usage**: ~2-4GB RAM total
- **Download Size**: ~1-2GB for all models
- **Inference Speed**: Fast (1-5 seconds per request)
- **Accuracy**: Good for basic tasks

### Production
- **Memory Usage**: ~8-16GB RAM total
- **Download Size**: ~4-8GB for all models
- **Inference Speed**: Moderate (5-15 seconds per request)
- **Accuracy**: Excellent for complex tasks

## Fallback Strategy

Each agent has a fallback model in case the primary model fails:

1. **Primary Model**: Agent-specific optimized model
2. **Fallback Model**: Smaller, more reliable model
3. **Hardcoded Response**: Simple text response if all models fail

## Installation

### Local Testing
```bash
pip install transformers torch accelerate
```

### Production
```bash
pip install transformers torch accelerate sentencepiece
```

## Usage Examples

### Basic Usage
```python
from repo_runner.llm.llm_utils import generate_code_with_llm

# Generate code with detection agent
response = generate_code_with_llm("Analyze this repository", "detection_agent")
```

### Custom Model
```python
import os
os.environ['DETECTION_AGENT_MODEL'] = 'microsoft/DialoGPT-large'

response = generate_code_with_llm("Analyze this repository", "detection_agent")
```

## Troubleshooting

### Common Issues

1. **Out of Memory**: Use smaller models for local testing
2. **Slow Inference**: Reduce max_tokens or use smaller models
3. **Model Download**: Ensure internet connection for first run
4. **CUDA Issues**: Use CPU-only mode for testing

### Solutions

1. **Memory Issues**: Switch to DialoGPT-small models
2. **Speed Issues**: Reduce max_tokens in configuration
3. **Download Issues**: Use cached models or offline mode
4. **CUDA Issues**: Set `torch.device('cpu')` for testing

## Model Performance Metrics

| Model | Parameters | Memory (GB) | Speed (req/s) | Accuracy |
|-------|------------|-------------|---------------|----------|
| DialoGPT-small | 117M | 0.5 | 10-20 | Good |
| DialoGPT-medium | 345M | 1.5 | 5-10 | Very Good |
| DialoGPT-large | 774M | 3.0 | 2-5 | Excellent |

## Best Practices

1. **Start with local models** for development and testing
2. **Use production models** for final deployment
3. **Monitor memory usage** and adjust accordingly
4. **Cache models** to avoid repeated downloads
5. **Use fallbacks** for reliability
6. **Test thoroughly** with different model sizes 