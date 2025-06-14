"""LiteLLM configuration for GitHub Models."""

from typing import Any

# GitHub Models configuration for LiteLLM
GITHUB_MODELS_CONFIG: dict[str, list[dict[str, Any]]] = {
    'model_list': [
        # OpenAI Models via GitHub
        {
            'model_name': 'github/openai/gpt-4.1',
            'litellm_params': {
                'model': 'openai/gpt-4.1',
                'api_base': 'https://models.github.ai/v1',
                'custom_llm_provider': 'github',
            },
        },
        {
            'model_name': 'github/openai/gpt-4o',
            'litellm_params': {
                'model': 'openai/gpt-4o',
                'api_base': 'https://models.github.ai/v1',
                'custom_llm_provider': 'github',
            },
        },
        {
            'model_name': 'github/openai/o1',
            'litellm_params': {
                'model': 'openai/o1',
                'api_base': 'https://models.github.ai/v1',
                'custom_llm_provider': 'github',
            },
        },
        {
            'model_name': 'github/openai/o3',
            'litellm_params': {
                'model': 'openai/o3',
                'api_base': 'https://models.github.ai/v1',
                'custom_llm_provider': 'github',
            },
        },
        # Meta Models via GitHub
        {
            'model_name': 'github/meta/llama-3.3-70b-instruct',
            'litellm_params': {
                'model': 'meta/llama-3.3-70b-instruct',
                'api_base': 'https://models.github.ai/v1',
                'custom_llm_provider': 'github',
            },
        },
        # Mistral Models via GitHub
        {
            'model_name': 'github/mistral-ai/mistral-large-2411',
            'litellm_params': {
                'model': 'mistral-ai/mistral-large-2411',
                'api_base': 'https://models.github.ai/v1',
                'custom_llm_provider': 'github',
            },
        },
        # DeepSeek Models via GitHub
        {
            'model_name': 'github/deepseek/deepseek-v3-0324',
            'litellm_params': {
                'model': 'deepseek/deepseek-v3-0324',
                'api_base': 'https://models.github.ai/v1',
                'custom_llm_provider': 'github',
            },
        },
    ]
}


def configure_litellm_for_github():
    """Configure LiteLLM to support GitHub models."""
    try:
        import litellm

        # Set GitHub models configuration
        for model_config in GITHUB_MODELS_CONFIG['model_list']:
            model_name = model_config['model_name']
            model_config['litellm_params']

            # Register the model with LiteLLM
            if hasattr(litellm, 'model_list'):
                if not any(
                    m.get('model_name') == model_name for m in litellm.model_list
                ):
                    litellm.model_list.append(model_config)

        # Set GitHub API configuration
        litellm.github_api_base = 'https://models.github.ai/v1'

        return True
    except Exception as e:
        print(f'Failed to configure LiteLLM for GitHub: {e}')
        return False


def get_github_model_config(model_name: str) -> dict[str, Any]:
    """Get configuration for a specific GitHub model.

    Args:
        model_name: The model name (e.g., "github/openai/gpt-4o")

    Returns:
        Configuration dictionary for the model
    """
    for config in GITHUB_MODELS_CONFIG['model_list']:
        if config['model_name'] == model_name:
            return config['litellm_params']

    # Default configuration for GitHub models
    if model_name.startswith('github/'):
        actual_model = model_name[7:]  # Remove "github/" prefix
        return {
            'model': actual_model,
            'api_base': 'https://models.github.ai/v1',
            'custom_llm_provider': 'github',
        }

    return {}


# Initialize configuration when module is imported
configure_litellm_for_github()
