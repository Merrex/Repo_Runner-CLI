import os
import json
import subprocess
from typing import Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# === FREE, ACCESSIBLE MODEL CONFIGURATION ===
# All models are free, open-source, and don't require authentication
AGENT_LLM_CONFIG = {
    'detection_agent': {
        'model_name': os.getenv('DETECTION_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('DETECTION_TOKEN', None),
        'max_tokens': 512,
        'temperature': 0.1,
        'max_input_length': 2048
    },
    'requirements_agent': {
        'model_name': os.getenv('REQUIREMENTS_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('REQUIREMENTS_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
    },
    'setup_agent': {
        'model_name': os.getenv('SETUP_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('SETUP_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
    },
    'fixer_agent': {
        'model_name': os.getenv('FIXER_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('FIXER_TOKEN', None),
        'max_tokens': 768,
        'temperature': 0.1,
        'max_input_length': 3072
    },
    'db_agent': {
        'model_name': os.getenv('DB_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('DB_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
    },
    'health_agent': {
        'model_name': os.getenv('HEALTH_MODEL', 'microsoft/DialoGPT-small'),
        'token': os.getenv('HEALTH_TOKEN', None),
        'max_tokens': 512,
        'temperature': 0.1,
        'max_input_length': 2048
    },
    'runner_agent': {
        'model_name': os.getenv('RUNNER_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('RUNNER_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
    },
}

# === ADVANCED MODEL CONFIGURATION (Optional) ===
# For users who want to use more powerful models with tokens
ADVANCED_MODEL_CONFIG = {
    'detection_agent': {
        'model_name': 'microsoft/DialoGPT-large',
        'token': None,
        'max_tokens': 1024,
        'temperature': 0.1,
        'max_input_length': 4096
    },
    'requirements_agent': {
        'model_name': 'microsoft/DialoGPT-large',
        'token': None,
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192
    },
    'setup_agent': {
        'model_name': 'microsoft/DialoGPT-large',
        'token': None,
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192
    },
    'fixer_agent': {
        'model_name': 'microsoft/DialoGPT-large',
        'token': None,
        'max_tokens': 1536,
        'temperature': 0.1,
        'max_input_length': 6144
    },
    'db_agent': {
        'model_name': 'microsoft/DialoGPT-large',
        'token': None,
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192
    },
    'health_agent': {
        'model_name': 'microsoft/DialoGPT-medium',
        'token': None,
        'max_tokens': 1024,
        'temperature': 0.1,
        'max_input_length': 4096
    },
    'runner_agent': {
        'model_name': 'microsoft/DialoGPT-large',
        'token': None,
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192
    },
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache for loaded pipelines per model
_llm_pipes = {}

# Model configuration for local testing (smaller models)
LOCAL_MODEL_CONFIG = {
    'detection_agent': {
        'model': 'microsoft/DialoGPT-small',  # 117M parameters
        'max_tokens': 512,
        'temperature': 0.3,
        'fallback': 'gpt2'
    },
    'requirements_agent': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.4,
        'fallback': 'microsoft/DialoGPT-small'
    },
    'setup_agent': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-small'
    },
    'db_agent': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-small'
    },
    'runner_agent': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-small'
    },
    'health_agent': {
        'model': 'microsoft/DialoGPT-small',  # 117M parameters
        'max_tokens': 512,
        'temperature': 0.2,
        'fallback': 'gpt2'
    },
    'fixer_agent': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.4,
        'fallback': 'microsoft/DialoGPT-small'
    },
    'orchestrator': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-small'
    }
}

def get_model_config(agent_name: str) -> Dict[str, Any]:
    """Get model configuration for an agent."""
    # Use local config for testing, can be overridden by environment
    config = LOCAL_MODEL_CONFIG.get(agent_name, LOCAL_MODEL_CONFIG['detection_agent'])
    
    # Allow environment override
    env_model = os.getenv(f'{agent_name.upper()}_MODEL')
    if env_model:
        config['model'] = env_model
    
    return config

def get_llm_pipeline(agent_name: str):
    """Get LLM pipeline with fallback to free models."""
    # Try to get token from environment
    token = os.getenv(f'{agent_name.upper()}_TOKEN')
    
    # Use free models by default
    config = AGENT_LLM_CONFIG.get(agent_name, AGENT_LLM_CONFIG['setup_agent'])
    model_name = config['model_name']
    cache_key = (model_name, token)
    
    if cache_key in _llm_pipes:
        return _llm_pipes[cache_key]
    
    try:
        # Load tokenizer with appropriate settings
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=token) if token else AutoTokenizer.from_pretrained(model_name)
        
        # Set pad token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model with appropriate settings
        model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32, 
            token=token,
            device_map="auto" if DEVICE=="cuda" else None,
            low_cpu_mem_usage=True
        ) if token else AutoModelForCausalLM.from_pretrained(
            model_name, 
            torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32,
            device_map="auto" if DEVICE=="cuda" else None,
            low_cpu_mem_usage=True
        )
        
        # Create pipeline
        pipe = pipeline(
            "text-generation", 
            model=model, 
            tokenizer=tokenizer, 
            device=0 if DEVICE=="cuda" else -1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        _llm_pipes[cache_key] = pipe
        return pipe
        
    except Exception as e:
        print(f"Failed to load model {model_name} for {agent_name}: {e}")
        # Fallback to a smaller, more reliable model
        fallback_config = {
            'model_name': 'microsoft/DialoGPT-small',
            'max_tokens': 256,
            'temperature': 0.2,
            'max_input_length': 1024
        }
        return _create_fallback_pipeline(fallback_config)

def _create_fallback_pipeline(config):
    """Create a fallback pipeline with a smaller model."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
        model = AutoModelForCausalLM.from_pretrained(
            config['model_name'], 
            torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32
        )
        
        pipe = pipeline(
            "text-generation", 
            model=model, 
            tokenizer=tokenizer, 
            device=0 if DEVICE=="cuda" else -1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        return pipe
    except Exception as e:
        print(f"Fallback pipeline also failed: {e}")
        return None

def generate_code_with_llm(prompt: str, agent_name: str, max_new_tokens: int = 100) -> str:
    """Generate code using LLM with proper error handling."""
    try:
        pipe = get_llm_pipeline(agent_name)
        if pipe is None:
            return f"# LLM not available for {agent_name}\n# Manual intervention required"
        
        # Generate response
        response = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.2,
            pad_token_id=pipe.tokenizer.eos_token_id
        )
        
        return response[0]['generated_text']
        
    except Exception as e:
        print(f"Error generating code for {agent_name}: {e}")
        return f"# Error in {agent_name}: {str(e)}\n# Manual intervention required"

def setup_huggingface_token():
    """Setup Hugging Face token for advanced models."""
    print("🔑 Hugging Face Token Setup")
    print("=" * 40)
    print("For advanced models that require authentication, you can:")
    print("1. Get a free token from: https://huggingface.co/settings/tokens")
    print("2. Set environment variables:")
    print("   export DETECTION_TOKEN='your_token_here'")
    print("   export REQUIREMENTS_TOKEN='your_token_here'")
    print("   export SETUP_TOKEN='your_token_here'")
    print("   export FIXER_TOKEN='your_token_here'")
    print("   export DB_TOKEN='your_token_here'")
    print("   export HEALTH_TOKEN='your_token_here'")
    print("   export RUNNER_TOKEN='your_token_here'")
    print("\n3. Or create a .env file with your tokens")
    print("\nNote: Free models work without tokens!")

def list_available_models():
    """List available models for each agent."""
    print("📋 Available Models for Each Agent")
    print("=" * 40)
    
    models = {
        'detection_agent': ['microsoft/DialoGPT-small', 'microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
        'requirements_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
        'setup_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
        'fixer_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
        'db_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
        'health_agent': ['microsoft/DialoGPT-small', 'microsoft/DialoGPT-medium'],
        'runner_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large']
    }
    
    for agent, model_list in models.items():
        print(f"\n{agent.replace('_', ' ').title()}:")
        for model in model_list:
            print(f"  - {model}")
    
    print("\n💡 All models are free and don't require authentication!")
    print("💡 Set environment variables to use specific models:")
    print("   export DETECTION_MODEL='microsoft/DialoGPT-large'")

def analyze_with_llm(content: str, agent_name: str = 'default') -> Dict[str, Any]:
    """Analyze content using LLM with structured output."""
    prompt = f"""
    Analyze the following content and provide a structured response:
    
    {content}
    
    Provide your analysis in JSON format with appropriate keys.
    """
    
    try:
        response = generate_code_with_llm(prompt, agent_name)
        
        # Try to parse as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Return structured fallback
            return {
                'analysis': response,
                'status': 'completed',
                'agent': agent_name
            }
            
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed',
            'agent': agent_name
        } 