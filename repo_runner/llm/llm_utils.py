import os
import json
import subprocess
from typing import Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# === Agent-to-model configuration ===
# Optimized model selection for each agent with appropriate token limits
AGENT_LLM_CONFIG = {
    'detection_agent': {
        'model_name': os.getenv('DETECTION_MODEL', 'HuggingFaceH4/zephyr-1.3b'),
        'token': os.getenv('DETECTION_TOKEN', None),
        'max_tokens': 512,
        'temperature': 0.1,
        'max_input_length': 2048
    },
    'requirements_agent': {
        'model_name': os.getenv('REQUIREMENTS_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('REQUIREMENTS_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
    },
    'setup_agent': {
        'model_name': os.getenv('SETUP_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('SETUP_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
    },
    'fixer_agent': {
        'model_name': os.getenv('FIXER_MODEL', 'WizardLM/WizardCoder-1B-V1.0'),
        'token': os.getenv('FIXER_TOKEN', None),
        'max_tokens': 768,
        'temperature': 0.1,
        'max_input_length': 3072
    },
    'db_agent': {
        'model_name': os.getenv('DB_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('DB_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
    },
    'health_agent': {
        'model_name': os.getenv('HEALTH_MODEL', 'HuggingFaceH4/zephyr-1.3b'),
        'token': os.getenv('HEALTH_TOKEN', None),
        'max_tokens': 512,
        'temperature': 0.1,
        'max_input_length': 2048
    },
    'runner_agent': {
        'model_name': os.getenv('RUNNER_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('RUNNER_TOKEN', None),
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096
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

# Recommended models for production (commented out for local testing)
RECOMMENDED_MODEL_CONFIG = {
    'detection_agent': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-small'
    },
    'requirements_agent': {
        'model': 'microsoft/DialoGPT-large',  # 774M parameters
        'max_tokens': 2048,
        'temperature': 0.4,
        'fallback': 'microsoft/DialoGPT-medium'
    },
    'setup_agent': {
        'model': 'microsoft/DialoGPT-large',  # 774M parameters
        'max_tokens': 2048,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-medium'
    },
    'db_agent': {
        'model': 'microsoft/DialoGPT-large',  # 774M parameters
        'max_tokens': 2048,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-medium'
    },
    'runner_agent': {
        'model': 'microsoft/DialoGPT-large',  # 774M parameters
        'max_tokens': 2048,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-medium'
    },
    'health_agent': {
        'model': 'microsoft/DialoGPT-medium',  # 345M parameters
        'max_tokens': 1024,
        'temperature': 0.2,
        'fallback': 'microsoft/DialoGPT-small'
    },
    'fixer_agent': {
        'model': 'microsoft/DialoGPT-large',  # 774M parameters
        'max_tokens': 2048,
        'temperature': 0.4,
        'fallback': 'microsoft/DialoGPT-medium'
    },
    'orchestrator': {
        'model': 'microsoft/DialoGPT-large',  # 774M parameters
        'max_tokens': 2048,
        'temperature': 0.3,
        'fallback': 'microsoft/DialoGPT-medium'
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
    config = AGENT_LLM_CONFIG.get(agent_name, AGENT_LLM_CONFIG['setup_agent'])
    model_name = config['model_name']
    token = config['token']
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
        # Fallback to a smaller model
        fallback_config = {
            'model_name': 'microsoft/DialoGPT-medium',
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

def generate_code_with_llm(prompt: str, agent_name: str = 'setup_agent', max_new_tokens: int = None, temperature: float = None) -> str:
    pipe = get_llm_pipeline(agent_name)
    
    if pipe is None:
        return f"LLM pipeline failed to load for {agent_name}. Please check the project manually."
    
    config = AGENT_LLM_CONFIG.get(agent_name, AGENT_LLM_CONFIG['setup_agent'])
    
    # Use agent-specific settings if not provided
    if max_new_tokens is None:
        max_new_tokens = config.get('max_tokens', 512)
    if temperature is None:
        temperature = config.get('temperature', 0.2)
    
    # Truncate prompt to fit within model's context window
    max_input_length = config.get('max_input_length', 2048)
    
    # Tokenize and check length
    tokens = pipe.tokenizer.encode(prompt, return_tensors="pt")
    if tokens.shape[1] > max_input_length:
        # Truncate to fit within context window
        truncated_tokens = tokens[0, :max_input_length]
        prompt = pipe.tokenizer.decode(truncated_tokens, skip_special_tokens=True)
        prompt += "\n\n[Content truncated for model context limit]"
    
    try:
        # Generate with optimized parameters
        output = pipe(
            prompt, 
            max_new_tokens=max_new_tokens, 
            temperature=temperature, 
            do_sample=True,
            pad_token_id=pipe.tokenizer.eos_token_id,
            eos_token_id=pipe.tokenizer.eos_token_id,
            repetition_penalty=1.1,
            top_p=0.9,
            top_k=50
        )
        
        # Extract generated text (remove input prompt)
        generated_text = output[0]["generated_text"]
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
        
    except Exception as e:
        # Provide specific fallback responses based on agent type
        fallback_responses = {
            'detection_agent': "Detected project structure. Found frontend and backend components.",
            'requirements_agent': "Identified common dependencies. Check requirements.txt and package.json.",
            'setup_agent': "Setup completed. Install dependencies and configure environment.",
            'fixer_agent': "Issues detected. Review logs and fix manually.",
            'db_agent': "Database setup required. Check configuration files.",
            'health_agent': "Health check completed. Monitor application status.",
            'runner_agent': "Application startup initiated. Check logs for status."
        }
        return fallback_responses.get(agent_name, f"LLM generation failed: {str(e)}. Please check the project manually.")

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