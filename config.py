# Configuration for models and their capabilities

# Available models with their IDs
AVAILABLE_MODELS = {
    "OpenAI GPT 4.1 Nano": "gpt-4.1-nano",
    "OpenAI GPT 4.1 Mini": "gpt-4.1-mini",
    "Google Gemini 2.5 Pro Exp": "gemini-2.5-pro-exp-03-25",
    "Google Gemini 2.0 Flash": "gemini-2.0-flash-001",
    "Meta Llama 4 Scout": "llama-4-scout-17b-16e-instruct",
    "Meta Llama 4 Maverick": "llama-4-maverick-17b-128e-instruct",
    "Meta Llama 3.3 70b": "llama-3.3-70b-versatile",
    "DeepSeek R1 Distilled 70B": "deepseek-r1-distill-llama-70b",
    "Qwen QwQ 32B": "qwen-qwq-32b",
    "Mistral Saba 24B": "mistral-saba-24b"
}

# Model capabilities for features
MODEL_CAPABILITIES = {
    "OpenAI GPT 4.1 Nano": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "OpenAI GPT 4.1 Mini": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "Google Gemini 2.5 Pro Exp": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": True,
        "Code Generation": True
    },
    "Google Gemini 2.0 Flash": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "Meta Llama 4 Scout": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "Meta Llama 4 Maverick": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "Meta Llama 3.3 70b": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "DeepSeek R1 Distilled 70B": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "Qwen QwQ 32B": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    },
    "Mistral Saba 24B": {
        "Text Generation": True,
        "File Analysis": True,
        "Image Generation": False,
        "Code Generation": True
    }
}

# Map for selecting appropriate model for special tasks
SPECIALIZED_MODELS = {
    "image_generation": "gemini-2.5-pro-exp-03-25",  # Default model for image generation
    "code_analysis": "gpt-4.1-mini",                 # Default model for code analysis
    "document_analysis": "llama-4-maverick-17b-128e-instruct"  # Default model for document analysis
}

# API endpoints
API_ENDPOINTS = {
    "chat": "https://api.euron.one/api/v1/euri/alpha/chat/completions",
    "image": "https://api.euron.one/api/v1/euri/alpha/images/generate"  # Assuming this endpoint for image generation
}
