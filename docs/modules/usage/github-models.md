# GitHub Models Integration

OpenHands now supports GitHub Models as an LLM provider, offering access to a wide variety of state-of-the-art models from different providers through a single GitHub API token. This integration includes automatic fallback when rate limits are hit, ensuring uninterrupted operation.

## Features

- **Wide Model Selection**: Access to 50+ models from OpenAI, Meta, Microsoft, Mistral, DeepSeek, xAI, and more
- **Automatic Fallback**: When a model hits its rate limit, OpenHands automatically switches to another available model in the same tier
- **Rate Limit Management**: Intelligent handling of different rate limit tiers (low, high, custom, embeddings)
- **Single API Key**: Use one GitHub token to access all available models
- **Cost Optimization**: Automatic switching to available models helps optimize costs and availability

## Available Models

GitHub Models provides access to models from multiple providers:

### OpenAI Models
- **GPT-4.1**: Latest GPT-4 with enhanced capabilities
- **GPT-4o**: Multimodal model with text, image, and audio support
- **o1/o3 Series**: Advanced reasoning models
- **o4-mini**: Cost-effective reasoning model

### Meta Models
- **Llama 3.3 70B**: High-performance instruction-following model
- **Llama 4 Maverick/Scout**: Latest Llama 4 variants with multimodal capabilities
- **Llama 3.1 405B**: Largest open-source model

### Microsoft Models
- **Phi-4**: Efficient small language model
- **MAI-DS-R1**: Enhanced reasoning model
- **Phi-4 Multimodal**: First small model with text, audio, and image inputs

### Other Providers
- **DeepSeek-R1**: Advanced reasoning model
- **Mistral Large/Medium**: High-performance European models
- **Grok 3/3-Mini**: xAI's latest models
- **Cohere Command R+**: Enterprise-grade RAG-optimized model
- **AI21 Jamba 1.5**: Long-context multilingual model

## Setup Instructions

### 1. Get a GitHub Token

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select the `models:read` scope
4. Generate and copy your token

### 2. Configure OpenHands

#### Using the UI (Recommended)

1. Start OpenHands using Docker:
   ```bash
   docker run -it --rm --pull=always \
       -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.43-nikolaik \
       -e LOG_ALL_EVENTS=true \
       -v /var/run/docker.sock:/var/run/docker.sock \
       -v ~/.openhands-state:/.openhands-state \
       -p 3000:3000 \
       --add-host host.docker.internal:host-gateway \
       --name openhands-app \
       docker.all-hands.dev/all-hands-ai/openhands:0.43
   ```

2. Open [http://localhost:3000](http://localhost:3000)
3. Click the Settings (gear) icon
4. In the LLM tab:
   - **Provider**: Select "GitHub Models"
   - **Model**: Choose from available GitHub models (e.g., `openai/gpt-4.1`)
   - **API Key**: Enter your GitHub token
5. Click "Save Changes"

#### Using Configuration File

Create or update your `config.toml`:

```toml
[llm]
model = "github/openai/gpt-4.1"
api_key = "your-github-token-here"
base_url = "https://models.github.ai"
custom_llm_provider = "openai"

# Optional: Configure fallback behavior
num_retries = 3
retry_min_wait = 5
retry_max_wait = 30
```

#### Using Environment Variables

```bash
export LLM_MODEL="github/openai/gpt-4.1"
export LLM_API_KEY="your-github-token-here"
export LLM_BASE_URL="https://models.github.ai"
export LLM_CUSTOM_LLM_PROVIDER="openai"
```

### 3. Running on Mac M1 with Docker

For Mac M1 users, ensure you have Docker Desktop installed and configured:

```bash
# Pull the latest images
docker pull docker.all-hands.dev/all-hands-ai/runtime:0.43-nikolaik
docker pull docker.all-hands.dev/all-hands-ai/openhands:0.43

# Run with GitHub Models configuration
docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.43-nikolaik \
    -e LLM_MODEL="github/openai/gpt-4.1" \
    -e LLM_API_KEY="your-github-token-here" \
    -e LLM_BASE_URL="https://models.github.ai" \
    -e LLM_CUSTOM_LLM_PROVIDER="openai" \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.43
```

## Rate Limiting and Fallback

GitHub Models has different rate limit tiers:

- **Low Tier**: Higher rate limits, suitable for development and testing
- **High Tier**: Lower rate limits, premium models
- **Custom Tier**: Special rate limits for reasoning models
- **Embeddings Tier**: Optimized for embedding models

When a model hits its rate limit, OpenHands automatically:

1. Detects the rate limit error
2. Marks the current model as temporarily unavailable
3. Finds another model in the same tier
4. Switches to the fallback model seamlessly
5. Continues processing without interruption

### Example Fallback Scenario

If you're using `github/openai/gpt-4.1` (high tier) and hit a rate limit, OpenHands might automatically switch to:
- `github/meta/llama-3.3-70b-instruct`
- `github/mistral-ai/mistral-large-2411`
- `github/deepseek/deepseek-v3-0324`

The system will cycle through available models until it finds one that's not rate-limited.

## Model Selection Guidelines

### For General Use
- **github/openai/gpt-4.1**: Best overall performance
- **github/meta/llama-3.3-70b-instruct**: Open-source alternative
- **github/mistral-ai/mistral-large-2411**: European option with strong reasoning

### For Coding Tasks
- **github/openai/gpt-4.1**: Excellent code generation
- **github/mistral-ai/codestral-2501**: Specialized for coding
- **github/deepseek/deepseek-v3-0324**: Strong coding capabilities

### For Reasoning Tasks
- **github/openai/o3**: Advanced reasoning
- **github/microsoft/mai-ds-r1**: Enhanced reasoning with safety
- **github/deepseek/deepseek-r1**: Open-source reasoning model

### For Cost-Effective Use
- **github/openai/gpt-4.1-mini**: Smaller, faster GPT-4.1
- **github/microsoft/phi-4**: Efficient small model
- **github/mistral-ai/ministral-3b**: Ultra-efficient model

## Troubleshooting

### Common Issues

1. **"Invalid API Key" Error**
   - Ensure your GitHub token has the `models:read` scope
   - Verify the token is not expired
   - Check that you're using a personal access token, not a fine-grained token

2. **"Model Not Found" Error**
   - Verify the model name is correct (use `github/provider/model` format)
   - Check that the model is available in your region
   - Try a different model from the same provider

3. **Rate Limiting Issues**
   - The automatic fallback should handle this, but if it persists:
   - Try using models from the "low" tier
   - Wait a few minutes before retrying
   - Consider using multiple GitHub accounts with different tokens

4. **Connection Errors**
   - Ensure you have internet connectivity
   - Check if GitHub Models API is accessible from your network
   - Verify the base URL is set to `https://models.github.ai`

### Debugging

Enable debug logging to see fallback behavior:

```bash
export LOG_ALL_EVENTS=true
export OPENHANDS_LOG_LEVEL=DEBUG
```

Check the logs for messages like:
- "Rate limit hit for github/openai/gpt-4.1, attempting fallback"
- "Switching to fallback model: github/meta/llama-3.3-70b-instruct"
- "Successfully used fallback model"

## Advanced Configuration

### Custom Fallback Strategy

You can configure multiple LLM configs for more control:

```toml
[llm]
model = "github/openai/gpt-4.1"
api_key = "your-github-token"
base_url = "https://models.github.ai"
custom_llm_provider = "openai"

[llm.fallback1]
model = "github/meta/llama-3.3-70b-instruct"
api_key = "your-github-token"
base_url = "https://models.github.ai"
custom_llm_provider = "openai"

[llm.fallback2]
model = "github/mistral-ai/mistral-large-2411"
api_key = "your-github-token"
base_url = "https://models.github.ai"
custom_llm_provider = "openai"
```

### Performance Tuning

For optimal performance with GitHub Models:

```toml
[llm]
model = "github/openai/gpt-4.1"
api_key = "your-github-token"
base_url = "https://models.github.ai"
custom_llm_provider = "openai"

# Optimize for GitHub Models
timeout = 60
num_retries = 3
retry_min_wait = 5
retry_max_wait = 30
retry_multiplier = 2

# Model-specific settings
temperature = 0.1
max_output_tokens = 4096
top_p = 0.95
```

## Security Considerations

- Store your GitHub token securely
- Use environment variables or secure configuration files
- Regularly rotate your GitHub tokens
- Monitor your GitHub Models usage in the GitHub dashboard
- Be aware that GitHub Models may log requests for abuse prevention

## Support and Resources

- [GitHub Models Documentation](https://docs.github.com/en/models)
- [GitHub Models Marketplace](https://github.com/marketplace?type=models)
- [OpenHands GitHub Repository](https://github.com/All-Hands-AI/OpenHands)
- [OpenHands Discord Community](https://discord.gg/ESHStjSjD4)

For issues specific to GitHub Models integration, please file an issue on the OpenHands repository with the "github-models" label.