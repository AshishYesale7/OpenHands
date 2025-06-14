"""Tests for GitHub Models integration."""

from unittest.mock import Mock, patch

import httpx
import pytest

from openhands.llm.github_models import (
    GitHubModelsProvider,
    GitHubModelsRateLimitHandler,
    get_github_models_for_litellm,
)


class TestGitHubModelsProvider:
    """Test GitHub Models provider functionality."""

    def test_init(self):
        """Test provider initialization."""
        provider = GitHubModelsProvider('test-token')
        assert provider.api_key == 'test-token'
        assert provider.base_url == 'https://models.github.ai'
        assert provider._models_cache is None

    def test_get_headers(self):
        """Test API headers generation."""
        provider = GitHubModelsProvider('test-token')
        headers = provider._get_headers()

        expected_headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer test-token',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        assert headers == expected_headers

    @patch('httpx.get')
    def test_get_available_models_success(self, mock_get):
        """Test successful model fetching."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'id': 'openai/gpt-4.1',
                'name': 'OpenAI GPT-4.1',
                'publisher': 'OpenAI',
                'rate_limit_tier': 'high',
            },
            {
                'id': 'meta/llama-3.3-70b-instruct',
                'name': 'Llama-3.3-70B-Instruct',
                'publisher': 'Meta',
                'rate_limit_tier': 'high',
            },
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = GitHubModelsProvider('test-token')
        models = provider.get_available_models()

        assert len(models) == 2
        assert models[0]['id'] == 'openai/gpt-4.1'
        assert models[1]['id'] == 'meta/llama-3.3-70b-instruct'

        # Test caching
        models_cached = provider.get_available_models()
        assert models_cached == models
        assert mock_get.call_count == 1  # Should not call API again

    @patch('httpx.get')
    def test_get_available_models_error(self, mock_get):
        """Test model fetching with API error."""
        mock_get.side_effect = httpx.HTTPError('API Error')

        provider = GitHubModelsProvider('test-token')
        models = provider.get_available_models()

        assert models == []

    @patch('httpx.get')
    def test_get_models_by_tier(self, mock_get):
        """Test filtering models by rate limit tier."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {'id': 'openai/gpt-4.1', 'rate_limit_tier': 'high'},
            {'id': 'openai/gpt-4o-mini', 'rate_limit_tier': 'low'},
            {'id': 'meta/llama-3.3-70b-instruct', 'rate_limit_tier': 'high'},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = GitHubModelsProvider('test-token')
        high_tier_models = provider.get_models_by_tier('high')
        low_tier_models = provider.get_models_by_tier('low')

        assert len(high_tier_models) == 2
        assert len(low_tier_models) == 1
        assert high_tier_models[0]['id'] == 'openai/gpt-4.1'
        assert low_tier_models[0]['id'] == 'openai/gpt-4o-mini'

    @patch('httpx.get')
    def test_get_fallback_models(self, mock_get):
        """Test getting fallback models for a given model."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {'id': 'openai/gpt-4.1', 'rate_limit_tier': 'high'},
            {'id': 'meta/llama-3.3-70b-instruct', 'rate_limit_tier': 'high'},
            {'id': 'mistral-ai/mistral-large-2411', 'rate_limit_tier': 'high'},
            {'id': 'openai/gpt-4o-mini', 'rate_limit_tier': 'low'},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = GitHubModelsProvider('test-token')
        fallbacks = provider.get_fallback_models('github/openai/gpt-4.1')

        assert len(fallbacks) == 2  # Same tier, excluding current model
        assert 'github/meta/llama-3.3-70b-instruct' in fallbacks
        assert 'github/mistral-ai/mistral-large-2411' in fallbacks
        assert 'github/openai/gpt-4.1' not in fallbacks

    @patch('httpx.get')
    def test_get_litellm_model_list(self, mock_get):
        """Test getting models in LiteLLM format."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {'id': 'openai/gpt-4.1'},
            {'id': 'meta/llama-3.3-70b-instruct'},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = GitHubModelsProvider('test-token')
        models = provider.get_litellm_model_list()

        assert len(models) == 2
        assert 'github/openai/gpt-4.1' in models
        assert 'github/meta/llama-3.3-70b-instruct' in models

    def test_is_github_model(self):
        """Test GitHub model detection."""
        provider = GitHubModelsProvider('test-token')

        assert provider.is_github_model('github/openai/gpt-4.1') is True
        assert provider.is_github_model('openai/gpt-4.1') is False
        assert provider.is_github_model('anthropic/claude-3-5-sonnet') is False


class TestGitHubModelsRateLimitHandler:
    """Test rate limit handler functionality."""

    def test_init(self):
        """Test handler initialization."""
        provider = GitHubModelsProvider('test-token')
        handler = GitHubModelsRateLimitHandler(provider)

        assert handler.provider == provider
        assert handler._failed_models == {}

    def test_is_model_available_new_model(self):
        """Test availability check for new model."""
        provider = GitHubModelsProvider('test-token')
        handler = GitHubModelsRateLimitHandler(provider)

        assert handler.is_model_available('github/openai/gpt-4.1') is True

    def test_mark_model_failed_and_check_availability(self):
        """Test marking model as failed and checking availability."""
        provider = GitHubModelsProvider('test-token')
        handler = GitHubModelsRateLimitHandler(provider)

        model = 'github/openai/gpt-4.1'
        handler.mark_model_failed(model)

        assert handler.is_model_available(model) is False
        assert model in handler._failed_models

    @patch('time.time')
    def test_model_availability_after_timeout(self, mock_time):
        """Test model becomes available after timeout."""
        provider = GitHubModelsProvider('test-token')
        handler = GitHubModelsRateLimitHandler(provider)

        model = 'github/openai/gpt-4.1'

        # Mark as failed at time 0
        mock_time.return_value = 0
        handler.mark_model_failed(model)
        assert handler.is_model_available(model) is False

        # Check availability after timeout (300 seconds)
        mock_time.return_value = 301
        assert handler.is_model_available(model) is True
        assert model not in handler._failed_models

    @patch('httpx.get')
    def test_get_next_available_model(self, mock_get):
        """Test getting next available fallback model."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {'id': 'openai/gpt-4.1', 'rate_limit_tier': 'high'},
            {'id': 'meta/llama-3.3-70b-instruct', 'rate_limit_tier': 'high'},
            {'id': 'mistral-ai/mistral-large-2411', 'rate_limit_tier': 'high'},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = GitHubModelsProvider('test-token')
        handler = GitHubModelsRateLimitHandler(provider)

        # Mark first fallback as failed
        handler.mark_model_failed('github/meta/llama-3.3-70b-instruct')

        next_model = handler.get_next_available_model('github/openai/gpt-4.1')

        # Should get the second fallback since first is marked as failed
        assert next_model == 'github/mistral-ai/mistral-large-2411'

    @patch('httpx.get')
    def test_get_next_available_model_no_fallbacks(self, mock_get):
        """Test when no fallback models are available."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {'id': 'openai/gpt-4.1', 'rate_limit_tier': 'high'},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        provider = GitHubModelsProvider('test-token')
        handler = GitHubModelsRateLimitHandler(provider)
        next_model = handler.get_next_available_model('github/openai/gpt-4.1')

        assert next_model is None


class TestGitHubModelsIntegration:
    """Test integration functions."""

    @patch('openhands.llm.github_models.get_github_provider')
    def test_get_github_models_for_litellm_success(self, mock_get_provider):
        """Test successful model list retrieval for LiteLLM."""
        mock_provider = Mock()
        mock_provider.get_litellm_model_list.return_value = [
            'github/openai/gpt-4.1',
            'github/meta/llama-3.3-70b-instruct',
        ]
        mock_get_provider.return_value = mock_provider

        models = get_github_models_for_litellm('test-token')

        assert len(models) == 2
        assert 'github/openai/gpt-4.1' in models
        assert 'github/meta/llama-3.3-70b-instruct' in models

    @patch('openhands.llm.github_models.get_github_provider')
    def test_get_github_models_for_litellm_error(self, mock_get_provider):
        """Test error handling in model list retrieval."""
        mock_get_provider.side_effect = Exception('API Error')

        models = get_github_models_for_litellm('test-token')

        assert models == []


if __name__ == '__main__':
    pytest.main([__file__])
