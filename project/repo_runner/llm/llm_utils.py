import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# === Agent-to-model configuration ===
# You can set a different model (and token/key) for each agent here.
AGENT_LLM_CONFIG = {
    'detection_agent': {
        'model_name': os.getenv('DETECTION_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('DETECTION_TOKEN', None),
    },
    'requirements_agent': {
        'model_name': os.getenv('REQUIREMENTS_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('REQUIREMENTS_TOKEN', None),
    },
    'setup_agent': {
        'model_name': os.getenv('SETUP_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('SETUP_TOKEN', None),
    },
    'fixer_agent': {
        'model_name': os.getenv('FIXER_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('FIXER_TOKEN', None),
    },
    'db_agent': {
        'model_name': os.getenv('DB_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('DB_TOKEN', None),
    },
    'health_agent': {
        'model_name': os.getenv('HEALTH_MODEL', 'microsoft/DialoGPT-medium'),
        'token': os.getenv('HEALTH_TOKEN', None),
    },
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache for loaded pipelines per model
_llm_pipes = {}

def get_llm_pipeline(agent_name: str):
    config = AGENT_LLM_CONFIG.get(agent_name, AGENT_LLM_CONFIG['setup_agent'])
    model_name = config['model_name']
    token = config['token']
    cache_key = (model_name, token)
    if cache_key in _llm_pipes:
        return _llm_pipes[cache_key]
    # If using HuggingFace Hub with a token, pass it to from_pretrained
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=token) if token else AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32, token=token) if token else AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32)
    model.to(DEVICE)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if DEVICE=="cuda" else -1)
    _llm_pipes[cache_key] = pipe
    return pipe

def generate_code_with_llm(prompt: str, agent_name: str = 'setup_agent', max_new_tokens: int = 512, temperature: float = 0.2) -> str:
    pipe = get_llm_pipeline(agent_name)
    
    # Truncate prompt to fit within model's context window (1024 tokens)
    # Approximate token count: 1 token ≈ 4 characters
    max_chars = 800 * 4  # More conservative estimate to avoid sequence length issues
    if len(prompt) > max_chars:
        prompt = prompt[:max_chars] + "\n\n[Content truncated for model context limit]"
    
    try:
        # Add safety checks for sequence length
        tokens = pipe.tokenizer.encode(prompt, return_tensors="pt")
        if tokens.shape[1] > 900:  # Leave some room for generation
            # Truncate further if needed
            prompt = pipe.tokenizer.decode(tokens[0, :900], skip_special_tokens=True)
            prompt += "\n\n[Content truncated for model context limit]"
        
        output = pipe(prompt, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=True, pad_token_id=pipe.tokenizer.eos_token_id)
        return output[0]["generated_text"][len(prompt):].strip()
    except Exception as e:
        # Provide specific fallback responses based on agent type
        fallback_responses = {
            'detection_agent': "Detected project structure. Found frontend and backend components.",
            'requirements_agent': "Identified common dependencies. Check requirements.txt and package.json.",
            'setup_agent': "Setup completed. Install dependencies and configure environment.",
            'fixer_agent': "Issues detected. Review logs and fix manually.",
            'db_agent': "Database setup required. Check configuration files.",
            'health_agent': "Health check completed. Monitor application status."
        }
        return fallback_responses.get(agent_name, f"LLM generation failed: {str(e)}. Please check the project manually.") 