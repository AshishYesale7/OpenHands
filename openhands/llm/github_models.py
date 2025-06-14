"""GitHub Models provider for OpenHands.

This module provides integration with GitHub Models API, including automatic
fallback when rate limits are hit and support for multiple model tiers.
"""

import time
from typing import Any, Optional

import httpx

from openhands.core.logger import openhands_logger as logger


class GitHubModelsProvider:
    """GitHub Models provider with automatic fallback on rate limits."""

    def __init__(self, api_key: str, base_url: str = 'https://models.github.ai'):
        """Initialize GitHub Models provider.

        Args:
            api_key: GitHub token for API access
            base_url: Base URL for GitHub Models API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self._models_cache: Optional[list[dict[str, Any]]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = 300  # 5 minutes cache

    def _get_headers(self) -> dict[str, str]:
        """Get headers for GitHub API requests."""
        return {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {self.api_key}',
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def get_available_models(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """Get list of available GitHub models.

        Args:
            force_refresh: Force refresh of cached models

        Returns:
            List of model dictionaries with id, name, publisher, rate_limit_tier, etc.
        """
        current_time = time.time()

        # Return cached models if available and not expired
        if (
            not force_refresh
            and self._models_cache is not None
            and self._cache_timestamp is not None
            and current_time - self._cache_timestamp < self._cache_ttl
        ):
            return self._models_cache

        try:
            response = httpx.get(
                f'{self.base_url}/catalog/models',
                headers=self._get_headers(),
                timeout=10.0,
            )
            response.raise_for_status()

            models = response.json()
            self._models_cache = models
            self._cache_timestamp = current_time

            logger.info(f'Fetched {len(models)} GitHub models')
            return models

        except httpx.HTTPError as e:
            logger.error(f'Failed to fetch GitHub models: {e}')
            return self._models_cache or []

    def get_models_by_tier(self, tier: str) -> list[dict[str, Any]]:
        """Get models filtered by rate limit tier.

        Args:
            tier: Rate limit tier ('low', 'high', 'custom', 'embeddings')

        Returns:
            List of models in the specified tier
        """
        models = self.get_available_models()
        return [model for model in models if model.get('rate_limit_tier') == tier]

    def get_fallback_models(self, current_model: str) -> list[str]:
        """Get fallback models for the current model.

        Args:
            current_model: Current model ID (e.g., 'github/openai/gpt-4o')

        Returns:
            List of fallback model IDs in the same tier
        """
        # Extract the actual model ID from the litellm format
        if current_model.startswith('github/'):
            github_model_id = current_model[7:]  # Remove 'github/' prefix
        else:
            github_model_id = current_model

        models = self.get_available_models()
        current_model_info = None

        # Find current model info
        for model in models:
            if model['id'] == github_model_id:
                current_model_info = model
                break

        if not current_model_info:
            logger.warning(
                f'Current model {github_model_id} not found in GitHub models'
            )
            return []

        # Get models in the same tier, excluding the current model
        tier = current_model_info.get('rate_limit_tier', 'low')
        tier_models = self.get_models_by_tier(tier)

        fallback_models = []
        for model in tier_models:
            if model['id'] != github_model_id:
                # Return in litellm format
                fallback_models.append(f'github/{model["id"]}')

        logger.info(f'Found {len(fallback_models)} fallback models for {current_model}')
        return fallback_models

    def get_litellm_model_list(self) -> list[str]:
        """Get list of models in LiteLLM format.

        Returns:
            List of model names prefixed with 'github/'
        """
        models = self.get_available_models()
        return [f'github/{model["id"]}' for model in models]

    def is_github_model(self, model: str) -> bool:
        """Check if a model is a GitHub model.

        Args:
            model: Model name to check

        Returns:
            True if the model is a GitHub model
        """
        return model.startswith('github/')


class GitHubModelsRateLimitHandler:
    """Handler for GitHub Models rate limit with automatic fallback."""

    def __init__(self, provider: GitHubModelsProvider):
        """Initialize rate limit handler.

        Args:
            provider: GitHub Models provider instance
        """
        self.provider = provider
        self._failed_models: dict[str, float] = {}
        self._failure_timeout = 300  # 5 minutes timeout for failed models

    def is_model_available(self, model: str) -> bool:
        """Check if a model is available (not in cooldown).

        Args:
            model: Model name to check

        Returns:
            True if model is available
        """
        if model not in self._failed_models:
            return True

        # Check if cooldown period has passed
        current_time = time.time()
        if current_time - self._failed_models[model] > self._failure_timeout:
            del self._failed_models[model]
            return True

        return False

    def mark_model_failed(self, model: str) -> None:
        """Mark a model as failed due to rate limiting.

        Args:
            model: Model name that failed
        """
        self._failed_models[model] = time.time()
        logger.warning(f'Marked GitHub model {model} as rate limited')

    def get_next_available_model(self, current_model: str) -> Optional[str]:
        """Get the next available fallback model.

        Args:
            current_model: Current model that hit rate limit

        Returns:
            Next available model or None if no fallbacks available
        """
        fallback_models = self.provider.get_fallback_models(current_model)

        for model in fallback_models:
            if self.is_model_available(model):
                logger.info(f'Switching from {current_model} to {model}')
                return model

        logger.warning(f'No available fallback models for {current_model}')
        return None


# Global instances
_github_provider: Optional[GitHubModelsProvider] = None
_rate_limit_handler: Optional[GitHubModelsRateLimitHandler] = None


def get_github_provider(api_key: str) -> GitHubModelsProvider:
    """Get or create GitHub Models provider instance.

    Args:
        api_key: GitHub token for API access

    Returns:
        GitHubModelsProvider instance
    """
    global _github_provider
    if _github_provider is None or _github_provider.api_key != api_key:
        _github_provider = GitHubModelsProvider(api_key)
    return _github_provider


def get_rate_limit_handler(api_key: str) -> GitHubModelsRateLimitHandler:
    """Get or create rate limit handler instance.

    Args:
        api_key: GitHub token for API access

    Returns:
        GitHubModelsRateLimitHandler instance
    """
    global _rate_limit_handler
    provider = get_github_provider(api_key)
    if _rate_limit_handler is None or _rate_limit_handler.provider != provider:
        _rate_limit_handler = GitHubModelsRateLimitHandler(provider)
    return _rate_limit_handler


def get_github_models_for_litellm(api_key: str) -> list[str]:
    """Get GitHub models list for LiteLLM integration.

    Args:
        api_key: GitHub token for API access

    Returns:
        List of GitHub model names in LiteLLM format
    """
    try:
        provider = get_github_provider(api_key)
        return provider.get_litellm_model_list()
    except Exception as e:
        logger.error(f'Failed to get GitHub models: {e}')
        return []
