SUPPORTED_MODELS = [
    {
        "id": "gemini-1.5-pro",
        "name": "Google Gemini 1.5 Pro",
        "provider": "gemini",
        "litellm_model": "gemini/gemini-1.5-pro"
    },
    {
        "id": "gemini-1.5-flash",
        "name": "Google Gemini 1.5 Flash",
        "provider": "gemini",
        "litellm_model": "gemini/gemini-1.5-flash"
    },
    {
        "id": "claude-3.5-sonnet",
        "name": "Anthropic Claude 3.5 Sonnet",
        "provider": "anthropic",
        "litellm_model": "anthropic/claude-3-5-sonnet-20241022"
    },
    {
        "id": "gpt-4o",
        "name": "OpenAI GPT-4o",
        "provider": "openai",
        "litellm_model": "openai/gpt-4o"
    },
    {
        "id": "gpt-4o-mini",
        "name": "OpenAI GPT-4o Mini",
        "provider": "openai",
        "litellm_model": "openai/gpt-4o-mini"
    },
    {
        "id": "local-qwen",
        "name": "Ollama Qwen 2.5 Coder 7B (Local)",
        "provider": "ollama",
        "litellm_model": "ollama/qwen2.5-coder:7b",
        "default_base_url": "http://localhost:11434"
    },
    {
        "id": "local-llama3",
        "name": "Ollama Llama 3 8B (Local)",
        "provider": "ollama",
        "litellm_model": "ollama/llama3",
        "default_base_url": "http://localhost:11434"
    }
]
