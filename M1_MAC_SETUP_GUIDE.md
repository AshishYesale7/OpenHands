# 🚀 OpenHands with GitHub Models - M1 Mac Setup Guide

## 📋 Prerequisites

### 1. Install Required Tools
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop for Mac
brew install --cask docker

# Install Git (if not already installed)
brew install git

# Install Node.js and npm
brew install node

# Install Python 3.12+ (if not already installed)
brew install python@3.12

# Install Poetry for Python dependency management
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Get GitHub Token
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy the generated token (starts with `ghp_`)

## 🛠️ Method 1: Docker Setup (Recommended for M1 Mac)

### Quick Start with Docker
```bash
# Set your GitHub token
export GITHUB_TOKEN="your-github-token-here"

# Run OpenHands with GitHub Models
docker run -it --rm --pull=always \
    --platform linux/amd64 \
    -e LLM_MODEL="github/openai/gpt-4.1" \
    -e LLM_API_KEY="$GITHUB_TOKEN" \
    -e LLM_BASE_URL="https://models.github.ai/v1" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 3000:3000 \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:latest
```

### Alternative GitHub Models to Try
```bash
# High-tier models (production ready)
-e LLM_MODEL="github/openai/gpt-4o"
-e LLM_MODEL="github/meta/llama-3.3-70b-instruct"
-e LLM_MODEL="github/mistral-ai/mistral-large-2411"

# Low-tier models (development)
-e LLM_MODEL="github/openai/gpt-4o-mini"
-e LLM_MODEL="github/microsoft/phi-4"

# Reasoning models
-e LLM_MODEL="github/openai/o1"
-e LLM_MODEL="github/deepseek/deepseek-v3-0324"
```

### Access the Application
1. Open your browser and go to: `http://localhost:3000`
2. You should see the OpenHands interface
3. The GitHub Models integration will be available in the LLM settings

## 🔧 Method 2: Local Development Setup

### 1. Clone and Setup Repository
```bash
# Clone your fork (or the main repository)
git clone https://github.com/AshishYesale7/OpenHands.git
cd OpenHands

# Switch to the GitHub Models integration branch
git checkout github-models-integration-clean

# Install Python dependencies
make install-pre-commit-hooks
poetry install

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Environment Configuration
```bash
# Create environment file
cat > .env << EOF
LLM_MODEL=github/openai/gpt-4.1
LLM_API_KEY=your-github-token-here
LLM_BASE_URL=https://models.github.ai/v1
WORKSPACE_BASE=/tmp/workspace
EOF
```

### 3. Build and Run
```bash
# Build the entire project
make build

# Start the backend (in one terminal)
poetry run python -m openhands.server.listen

# Start the frontend (in another terminal)
cd frontend
npm run dev
```

### 4. Access the Application
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## 🧪 Testing GitHub Models Integration

### 1. Verify Models are Available
```bash
# Test GitHub Models API access
curl -H "Authorization: Bearer your-github-token" \
     https://models.github.ai/v1/models
```

### 2. Test in OpenHands UI
1. Open `http://localhost:3000`
2. Click on Settings (gear icon)
3. Go to "LLM Settings"
4. You should see GitHub Models information
5. Select a GitHub model from the dropdown
6. Enter your GitHub token
7. Test with a simple query

### 3. Test Automatic Fallback
1. Use a high-tier model like `github/openai/gpt-4.1`
2. Make multiple rapid requests to trigger rate limits
3. Watch the logs to see automatic fallback in action
4. Check that it switches to alternative models

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Docker Platform Issues on M1 Mac
```bash
# Always use --platform linux/amd64 for M1 Macs
docker run --platform linux/amd64 ...
```

#### 2. GitHub Token Issues
```bash
# Verify token has correct permissions
curl -H "Authorization: Bearer your-token" https://api.github.com/user

# Check token scopes
curl -H "Authorization: Bearer your-token" -I https://api.github.com/user
```

#### 3. Port Conflicts
```bash
# Check what's using port 3000
lsof -i :3000

# Use different port
docker run -p 3001:3000 ...
```

#### 4. Memory Issues on M1 Mac
```bash
# Increase Docker memory limit in Docker Desktop settings
# Recommended: 8GB+ for OpenHands
```

### Debug Mode
```bash
# Enable debug logging
export OPENHANDS_LOG_LEVEL=DEBUG

# Run with verbose output
docker run -e OPENHANDS_LOG_LEVEL=DEBUG ...
```

## 📊 Available GitHub Models

### High Tier (Production Ready)
- `github/openai/gpt-4.1` - Latest GPT-4 model
- `github/openai/gpt-4o` - Optimized GPT-4
- `github/meta/llama-3.3-70b-instruct` - Meta's latest
- `github/mistral-ai/mistral-large-2411` - Mistral flagship
- `github/ai21labs/jamba-1-5-large` - AI21 Labs model
- `github/cohere/command-r-plus` - Cohere's advanced model

### Low Tier (Development)
- `github/openai/gpt-4o-mini` - Lightweight GPT-4
- `github/microsoft/phi-4` - Microsoft's efficient model
- `github/mistral-ai/mistral-small-2412` - Compact Mistral

### Custom Tier (Reasoning)
- `github/openai/o1` - Advanced reasoning
- `github/openai/o1-mini` - Compact reasoning
- `github/openai/o3-mini` - Latest reasoning model
- `github/deepseek/deepseek-v3-0324` - DeepSeek reasoning

### Embeddings
- `github/openai/text-embedding-3-small`
- `github/openai/text-embedding-3-large`

## 🚀 Performance Tips

### 1. Model Selection Strategy
- **Development**: Start with low-tier models
- **Production**: Use high-tier models
- **Reasoning Tasks**: Use custom-tier models
- **Cost Optimization**: Mix tiers based on task complexity

### 2. Rate Limit Management
- The system automatically handles rate limits
- No manual intervention needed
- Fallback happens within the same tier when possible
- Original models re-enabled after 5-minute cooldown

### 3. Docker Optimization for M1 Mac
```bash
# Use multi-stage builds for faster startup
docker build --platform linux/amd64 -t openhands-local .

# Use volume mounts for development
docker run -v $(pwd):/workspace ...
```

## 📝 Configuration Examples

### Basic Configuration
```bash
export LLM_MODEL="github/openai/gpt-4.1"
export LLM_API_KEY="ghp_your_token_here"
export LLM_BASE_URL="https://models.github.ai/v1"
```

### Advanced Configuration with Fallback
```bash
# Primary model with automatic fallback enabled
export LLM_MODEL="github/openai/gpt-4.1"
export LLM_API_KEY="ghp_your_token_here"
export LLM_BASE_URL="https://models.github.ai/v1"
export OPENHANDS_LOG_LEVEL="INFO"
```

### Development Configuration
```bash
export LLM_MODEL="github/openai/gpt-4o-mini"
export LLM_API_KEY="ghp_your_token_here"
export LLM_BASE_URL="https://models.github.ai/v1"
export WORKSPACE_BASE="/tmp/openhands_workspace"
```

## 🎯 Next Steps

1. **Test the Integration**: Try different models and tasks
2. **Explore Fallback**: Trigger rate limits to see automatic switching
3. **Monitor Performance**: Check logs for fallback behavior
4. **Contribute**: Report issues or suggest improvements
5. **Scale Up**: Use in production with high-tier models

## 📞 Support

- **GitHub Issues**: [OpenHands Repository](https://github.com/All-Hands-AI/OpenHands/issues)
- **Documentation**: [docs.all-hands.dev](https://docs.all-hands.dev)
- **Discord**: [OpenHands Community](https://discord.gg/ESHStjSjD4)

---

**Happy Coding with OpenHands + GitHub Models! 🚀**