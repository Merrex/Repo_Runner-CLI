import os
import json
import subprocess
from typing import Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# === UNIVERSAL MODEL CONFIGURATION ===
# Supports public, gated, and paid models with proper authentication

# Default models (free, public)
DEFAULT_MODEL_CONFIG = {
    'detection_agent': {
        'model_name': 'microsoft/DialoGPT-medium',
        'max_tokens': 512,
        'temperature': 0.1,
        'max_input_length': 2048,
        'type': 'public'
    },
    'requirements_agent': {
        'model_name': 'microsoft/DialoGPT-medium',
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096,
        'type': 'public'
    },
    'setup_agent': {
        'model_name': 'microsoft/DialoGPT-medium',
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096,
        'type': 'public'
    },
    'fixer_agent': {
        'model_name': 'microsoft/DialoGPT-medium',
        'max_tokens': 768,
        'temperature': 0.1,
        'max_input_length': 3072,
        'type': 'public'
    },
    'db_agent': {
        'model_name': 'microsoft/DialoGPT-medium',
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096,
        'type': 'public'
    },
    'health_agent': {
        'model_name': 'microsoft/DialoGPT-small',
        'max_tokens': 512,
        'temperature': 0.1,
        'max_input_length': 2048,
        'type': 'public'
    },
    'runner_agent': {
        'model_name': 'microsoft/DialoGPT-medium',
        'max_tokens': 1024,
        'temperature': 0.2,
        'max_input_length': 4096,
        'type': 'public'
    },
}

# Advanced models (gated/paid) - require authentication
ADVANCED_MODEL_CONFIG = {
    'detection_agent': {
        'model_name': 'mistralai/Mistral-7B-Instruct-v0.2',
        'max_tokens': 1024,
        'temperature': 0.1,
        'max_input_length': 4096,
        'type': 'gated',
        'requires_token': True
    },
    'requirements_agent': {
        'model_name': 'mistralai/Mistral-7B-Instruct-v0.2',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'gated',
        'requires_token': True
    },
    'setup_agent': {
        'model_name': 'mistralai/Mistral-7B-Instruct-v0.2',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'gated',
        'requires_token': True
    },
    'fixer_agent': {
        'model_name': 'WizardLM/WizardCoder-1B-V1.0',
        'max_tokens': 1536,
        'temperature': 0.1,
        'max_input_length': 6144,
        'type': 'gated',
        'requires_token': True
    },
    'db_agent': {
        'model_name': 'mistralai/Mistral-7B-Instruct-v0.2',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'gated',
        'requires_token': True
    },
    'health_agent': {
        'model_name': 'HuggingFaceH4/zephyr-1.3b',
        'max_tokens': 1024,
        'temperature': 0.1,
        'max_input_length': 4096,
        'type': 'gated',
        'requires_token': True
    },
    'runner_agent': {
        'model_name': 'mistralai/Mistral-7B-Instruct-v0.2',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'gated',
        'requires_token': True
    },
}

# Premium models (paid APIs) - require API keys
PREMIUM_MODEL_CONFIG = {
    'detection_agent': {
        'model_name': 'gpt-3.5-turbo',
        'max_tokens': 1024,
        'temperature': 0.1,
        'max_input_length': 4096,
        'type': 'paid',
        'provider': 'openai',
        'requires_api_key': True
    },
    'requirements_agent': {
        'model_name': 'gpt-4',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'paid',
        'provider': 'openai',
        'requires_api_key': True
    },
    'setup_agent': {
        'model_name': 'gpt-4',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'paid',
        'provider': 'openai',
        'requires_api_key': True
    },
    'fixer_agent': {
        'model_name': 'gpt-4',
        'max_tokens': 1536,
        'temperature': 0.1,
        'max_input_length': 6144,
        'type': 'paid',
        'provider': 'openai',
        'requires_api_key': True
    },
    'db_agent': {
        'model_name': 'gpt-4',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'paid',
        'provider': 'openai',
        'requires_api_key': True
    },
    'health_agent': {
        'model_name': 'gpt-3.5-turbo',
        'max_tokens': 1024,
        'temperature': 0.1,
        'max_input_length': 4096,
        'type': 'paid',
        'provider': 'openai',
        'requires_api_key': True
    },
    'runner_agent': {
        'model_name': 'gpt-4',
        'max_tokens': 2048,
        'temperature': 0.2,
        'max_input_length': 8192,
        'type': 'paid',
        'provider': 'openai',
        'requires_api_key': True
    },
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache for loaded pipelines per model
_llm_pipes = {}

def get_model_config(agent_name: str) -> Dict[str, Any]:
    """Get model configuration for an agent with environment override."""
    # Check environment for model type preference
    model_type = os.getenv(f'{agent_name.upper()}_MODEL_TYPE', 'default')
    
    if model_type == 'advanced':
        config = ADVANCED_MODEL_CONFIG.get(agent_name, ADVANCED_MODEL_CONFIG['setup_agent'])
    elif model_type == 'premium':
        config = PREMIUM_MODEL_CONFIG.get(agent_name, PREMIUM_MODEL_CONFIG['setup_agent'])
    else:
        config = DEFAULT_MODEL_CONFIG.get(agent_name, DEFAULT_MODEL_CONFIG['setup_agent'])
    
    # Allow environment override for specific model
    env_model = os.getenv(f'{agent_name.upper()}_MODEL')
    if env_model:
        config['model_name'] = env_model
    
    return config

def get_authentication_for_model(agent_name: str, config: Dict[str, Any]) -> Optional[str]:
    """Get authentication token/key for a model."""
    model_type = config.get('type', 'public')
    
    if model_type == 'public':
        return None
    elif model_type == 'gated':
        # Try to get Hugging Face token
        token = os.getenv(f'{agent_name.upper()}_TOKEN')
        if not token:
            token = os.getenv('HUGGINGFACE_TOKEN')
        return token
    elif model_type == 'paid':
        # Try to get API key based on provider
        provider = config.get('provider', 'openai')
        if provider == 'openai':
            return os.getenv(f'{agent_name.upper()}_API_KEY') or os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            return os.getenv(f'{agent_name.upper()}_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        elif provider == 'google':
            return os.getenv(f'{agent_name.upper()}_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    return None

def get_llm_pipeline(agent_name: str):
    """Get LLM pipeline with universal model support."""
    config = get_model_config(agent_name)
    model_name = config['model_name']
    model_type = config.get('type', 'public')
    
    # Get authentication
    auth_token = get_authentication_for_model(agent_name, config)
    cache_key = (model_name, auth_token, model_type)
    
    if cache_key in _llm_pipes:
        return _llm_pipes[cache_key]
    
    try:
        if model_type == 'paid':
            # Handle paid API models
            return _create_api_pipeline(agent_name, config, auth_token)
        else:
            # Handle local models (public/gated)
            return _create_local_pipeline(agent_name, config, auth_token)
            
    except Exception as e:
        print(f"Failed to load model {model_name} for {agent_name}: {e}")
        # Fallback to a reliable public model
        return _create_fallback_pipeline(agent_name)

def _create_local_pipeline(agent_name: str, config: Dict[str, Any], token: Optional[str]):
    """Create pipeline for local models (public/gated)."""
    model_name = config['model_name']
    
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
    
    cache_key = (model_name, token, config.get('type', 'public'))
    _llm_pipes[cache_key] = pipe
    return pipe

def _create_api_pipeline(agent_name: str, config: Dict[str, Any], api_key: Optional[str]):
    """Create pipeline for paid API models."""
    model_name = config['model_name']
    provider = config.get('provider', 'openai')
    
    if not api_key:
        raise ValueError(f"API key required for {provider} model {model_name}")
    
    # Create API-based pipeline
    if provider == 'openai':
        return _create_openai_pipeline(agent_name, config, api_key)
    elif provider == 'anthropic':
        return _create_anthropic_pipeline(agent_name, config, api_key)
    elif provider == 'google':
        return _create_google_pipeline(agent_name, config, api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def _create_openai_pipeline(agent_name: str, config: Dict[str, Any], api_key: str):
    """Create OpenAI API pipeline."""
    try:
        import openai
        openai.api_key = api_key
        
        def generate_text(prompt, max_tokens=None, temperature=None):
            response = openai.ChatCompletion.create(
                model=config['model_name'],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or config.get('max_tokens', 100),
                temperature=temperature or config.get('temperature', 0.2)
            )
            return response.choices[0].message.content
        
        # Create a pipeline-like interface
        class OpenAIPipeline:
            def __init__(self, generate_func, config):
                self.generate = generate_func
                self.config = config
            
            def __call__(self, prompt, **kwargs):
                result = self.generate(prompt, **kwargs)
                return [{'generated_text': result}]
        
        pipe = OpenAIPipeline(generate_text, config)
        cache_key = (config['model_name'], api_key, 'paid')
        _llm_pipes[cache_key] = pipe
        return pipe
        
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")

def _create_anthropic_pipeline(agent_name: str, config: Dict[str, Any], api_key: str):
    """Create Anthropic API pipeline."""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=api_key)
        
        def generate_text(prompt, max_tokens=None, temperature=None):
            response = client.messages.create(
                model=config['model_name'],
                max_tokens=max_tokens or config.get('max_tokens', 100),
                temperature=temperature or config.get('temperature', 0.2),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        class AnthropicPipeline:
            def __init__(self, generate_func, config):
                self.generate = generate_func
                self.config = config
            
            def __call__(self, prompt, **kwargs):
                result = self.generate(prompt, **kwargs)
                return [{'generated_text': result}]
        
        pipe = AnthropicPipeline(generate_text, config)
        cache_key = (config['model_name'], api_key, 'paid')
        _llm_pipes[cache_key] = pipe
        return pipe
        
    except ImportError:
        raise ImportError("Anthropic package not installed. Run: pip install anthropic")

def _create_google_pipeline(agent_name: str, config: Dict[str, Any], api_key: str):
    """Create Google API pipeline."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(config['model_name'])
        
        def generate_text(prompt, max_tokens=None, temperature=None):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens or config.get('max_tokens', 100),
                    temperature=temperature or config.get('temperature', 0.2)
                )
            )
            return response.text
        
        class GooglePipeline:
            def __init__(self, generate_func, config):
                self.generate = generate_func
                self.config = config
            
            def __call__(self, prompt, **kwargs):
                result = self.generate(prompt, **kwargs)
                return [{'generated_text': result}]
        
        pipe = GooglePipeline(generate_text, config)
        cache_key = (config['model_name'], api_key, 'paid')
        _llm_pipes[cache_key] = pipe
        return pipe
        
    except ImportError:
        raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")

def _create_fallback_pipeline(agent_name: str):
    """Create a fallback pipeline with a reliable public model."""
    try:
        fallback_config = {
            'model_name': 'microsoft/DialoGPT-small',
            'max_tokens': 256,
            'temperature': 0.2,
            'max_input_length': 1024,
            'type': 'public'
        }
        return _create_local_pipeline(agent_name, fallback_config, None)
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
            pad_token_id=getattr(pipe, 'tokenizer', None) and pipe.tokenizer.eos_token_id
        )
        
        return response[0]['generated_text']
        
    except Exception as e:
        print(f"Error generating code for {agent_name}: {e}")
        return f"# Error in {agent_name}: {str(e)}\n# Manual intervention required"

def setup_model_authentication():
    """Setup authentication for different model types."""
    print("🔑 Universal Model Authentication Setup")
    print("=" * 50)
    
    print("\n📋 Model Types Supported:")
    print("1. 🆓 Public Models (Free, No Auth)")
    print("   - microsoft/DialoGPT-small")
    print("   - microsoft/DialoGPT-medium")
    print("   - microsoft/DialoGPT-large")
    
    print("\n2. 🔒 Gated Models (Free Token Required)")
    print("   - mistralai/Mistral-7B-Instruct-v0.2")
    print("   - HuggingFaceH4/zephyr-1.3b")
    print("   - WizardLM/WizardCoder-1B-V1.0")
    
    print("\n3. 💰 Paid Models (API Key Required)")
    print("   - OpenAI: gpt-3.5-turbo, gpt-4")
    print("   - Anthropic: claude-3-sonnet")
    print("   - Google: gemini-pro")
    
    print("\n🔧 Setup Instructions:")
    print("\nFor Gated Models (Hugging Face):")
    print("1. Get free token: https://huggingface.co/settings/tokens")
    print("2. Set environment variables:")
    print("   export DETECTION_TOKEN='hf_your_token'")
    print("   export REQUIREMENTS_TOKEN='hf_your_token'")
    
    print("\nFor Paid Models (OpenAI):")
    print("1. Get API key: https://platform.openai.com/api-keys")
    print("2. Set environment variables:")
    print("   export OPENAI_API_KEY='sk-your_key_here'")
    print("   export DETECTION_AGENT_MODEL_TYPE='premium'")
    
    print("\nFor Paid Models (Anthropic):")
    print("1. Get API key: https://console.anthropic.com/")
    print("2. Set environment variables:")
    print("   export ANTHROPIC_API_KEY='sk-ant-your_key_here'")
    print("   export DETECTION_AGENT_MODEL_TYPE='premium'")

def list_available_models():
    """List available models for each agent with type information."""
    print("📋 Universal Model Configuration")
    print("=" * 50)
    
    model_categories = {
        'Public (Free)': {
            'detection_agent': ['microsoft/DialoGPT-small', 'microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
            'requirements_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
            'setup_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
            'fixer_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
            'db_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
            'health_agent': ['microsoft/DialoGPT-small', 'microsoft/DialoGPT-medium'],
            'runner_agent': ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large']
        },
        'Gated (Free Token)': {
            'detection_agent': ['mistralai/Mistral-7B-Instruct-v0.2'],
            'requirements_agent': ['mistralai/Mistral-7B-Instruct-v0.2'],
            'setup_agent': ['mistralai/Mistral-7B-Instruct-v0.2'],
            'fixer_agent': ['WizardLM/WizardCoder-1B-V1.0'],
            'db_agent': ['mistralai/Mistral-7B-Instruct-v0.2'],
            'health_agent': ['HuggingFaceH4/zephyr-1.3b'],
            'runner_agent': ['mistralai/Mistral-7B-Instruct-v0.2']
        },
        'Paid (API Key)': {
            'detection_agent': ['gpt-3.5-turbo'],
            'requirements_agent': ['gpt-4'],
            'setup_agent': ['gpt-4'],
            'fixer_agent': ['gpt-4'],
            'db_agent': ['gpt-4'],
            'health_agent': ['gpt-3.5-turbo'],
            'runner_agent': ['gpt-4']
        }
    }
    
    for category, agents in model_categories.items():
        print(f"\n{category}:")
        for agent, models in agents.items():
            print(f"  {agent.replace('_', ' ').title()}:")
            for model in models:
                print(f"    - {model}")
    
    print("\n💡 Configuration:")
    print("1. Public models work out of the box")
    print("2. Gated models need Hugging Face token")
    print("3. Paid models need API keys")
    print("\nSet environment variables to use specific models:")
    print("  export DETECTION_MODEL='microsoft/DialoGPT-large'")
    print("  export DETECTION_AGENT_MODEL_TYPE='advanced'")

def analyze_with_llm(content: str, agent_name: str = 'default') -> Dict[str, Any]:
    """Analyze content using LLM with universal model support."""
    try:
        response = generate_code_with_llm(content, agent_name)
        return {
            'success': True,
            'response': response,
            'agent': agent_name,
            'model_type': 'universal'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'agent': agent_name,
            'model_type': 'universal'
        } 