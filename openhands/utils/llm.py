import warnings

import httpx

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import litellm

from openhands.core.config import AppConfig, LLMConfig
from openhands.core.logger import openhands_logger as logger
from openhands.llm import bedrock
from openhands.llm.github_models import get_github_models_for_litellm


def get_supported_llm_models(config: AppConfig) -> list[str]:
    """Get all models supported by LiteLLM.

    This function combines models from litellm and Bedrock, removing any
    error-prone Bedrock models.

    Returns:
        list[str]: A sorted list of unique model names.
    """
    litellm_model_list = litellm.model_list + list(litellm.model_cost.keys())
    litellm_model_list_without_bedrock = bedrock.remove_error_modelId(
        litellm_model_list
    )
    # TODO: for bedrock, this is using the default config
    llm_config: LLMConfig = config.get_llm_config()
    bedrock_model_list = []
    if (
        llm_config.aws_region_name
        and llm_config.aws_access_key_id
        and llm_config.aws_secret_access_key
    ):
        bedrock_model_list = bedrock.list_foundation_models(
            llm_config.aws_region_name,
            llm_config.aws_access_key_id.get_secret_value(),
            llm_config.aws_secret_access_key.get_secret_value(),
        )
    model_list = litellm_model_list_without_bedrock + bedrock_model_list

    # Add GitHub models if API key is available
    github_models = []
    for llm_config in config.llms.values():
        if llm_config.api_key and llm_config.api_key.get_secret_value():
            # Check if this might be a GitHub token (starts with ghp_, gho_, ghu_, ghs_, or github_pat_)
            api_key = llm_config.api_key.get_secret_value()
            if (
                api_key.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'github_pat_'))
                or llm_config.custom_llm_provider == 'github'
            ):
                try:
                    github_models = get_github_models_for_litellm(api_key)
                    logger.info(f'Added {len(github_models)} GitHub models')
                    break
                except Exception as e:
                    logger.debug(f'Failed to fetch GitHub models: {e}')

    model_list.extend(github_models)

    # Add Ollama models
    for llm_config in config.llms.values():
        ollama_base_url = llm_config.ollama_base_url
        if llm_config.model.startswith('ollama'):
            if not ollama_base_url:
                ollama_base_url = llm_config.base_url
        if ollama_base_url:
            ollama_url = ollama_base_url.strip('/') + '/api/tags'
            try:
                ollama_models_list = httpx.get(ollama_url, timeout=3).json()['models']  # noqa: ASYNC100
                for model in ollama_models_list:
                    model_list.append('ollama/' + model['name'])
                break
            except httpx.HTTPError as e:
                logger.error(f'Error getting OLLAMA models: {e}')

    return list(sorted(set(model_list)))
