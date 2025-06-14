# 🚀 Complete Local Setup Guide for M1 Mac - Enhanced OpenHands with GitHub Models

## 📋 Overview
This guide shows you how to:
1. Clone YOUR enhanced repository to your M1 Mac
2. Set it up in VSCode
3. Build your own Docker image with GitHub Models integration
4. Run it locally instead of using the official image

## 🛠️ Step 1: Prerequisites Setup

### Install Required Tools
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop for Mac (REQUIRED for building)
brew install --cask docker

# Install VSCode (if not already installed)
brew install --cask visual-studio-code

# Install Git, Node.js, Python
brew install git node python@3.12

# Install Poetry for Python dependency management
curl -sSL https://install.python-poetry.org | python3 -
```

### Start Docker Desktop
```bash
# Open Docker Desktop (MUST be running for builds)
open /Applications/Docker.app

# Wait for Docker to start, then verify
docker --version
docker info
```

## 🔄 Step 2: Clone Your Enhanced Repository

```bash
# Create a workspace directory
mkdir -p ~/workspace
cd ~/workspace

# Clone YOUR enhanced repository (not the original)
git clone https://github.com/AshishYesale7/OpenHands.git
cd OpenHands

# Switch to your enhanced branch
git checkout github-models-integration-clean

# Verify you have the GitHub Models integration
ls -la openhands/llm/github_models.py
ls -la frontend/src/components/features/settings/github-models-info.tsx
```

## 💻 Step 3: Open in VSCode

```bash
# Open the project in VSCode
code .

# Or if you prefer to open VSCode first, then:
# File > Open Folder > Select the OpenHands directory
```

### Recommended VSCode Extensions
Install these extensions for better development experience:
- Python
- Docker
- TypeScript and JavaScript Language Features
- Prettier - Code formatter
- GitLens

## 🐳 Step 4: Build Your Enhanced Docker Image

### Method A: Using the Project's Build Script (Recommended)
```bash
# Make sure you're in the project root
cd ~/workspace/OpenHands

# Build your enhanced image using the project's build system
./containers/build.sh -i openhands --load

# This creates: ghcr.io/all-hands-ai/openhands:dev (locally)
```

### Method B: Direct Docker Build
```bash
# Build directly with Docker (alternative method)
docker buildx build \
  --platform linux/amd64 \
  --load \
  -t openhands-enhanced:latest \
  -f containers/app/Dockerfile \
  .
```

### Method C: Using Our Custom Script
```bash
# Use the script we created earlier
chmod +x build-and-run.sh
export GITHUB_TOKEN="your-github-token-here"
./build-and-run.sh
```

## 🚀 Step 5: Run Your Enhanced Version

### Option 1: Run with Project's Built Image
```bash
# Set your GitHub token
export GITHUB_TOKEN="your-github-token-here"

# Run your locally built enhanced version
docker run -it --rm \
  --platform linux/amd64 \
  -e LLM_MODEL="github/openai/gpt-4.1" \
  -e LLM_API_KEY="$GITHUB_TOKEN" \
  -e LLM_BASE_URL="https://models.github.ai/v1" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  --name openhands-local \
  ghcr.io/all-hands-ai/openhands:dev
```

### Option 2: Run with Custom Tagged Image
```bash
# If you used Method B above
docker run -it --rm \
  --platform linux/amd64 \
  -e LLM_MODEL="github/openai/gpt-4.1" \
  -e LLM_API_KEY="$GITHUB_TOKEN" \
  -e LLM_BASE_URL="https://models.github.ai/v1" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  --name openhands-local \
  openhands-enhanced:latest
```

### Option 3: Using Docker Compose
```bash
# Create docker-compose.override.yml for local development
cat > docker-compose.override.yml << 'EOF'
version: '3.8'

services:
  openhands:
    image: ghcr.io/all-hands-ai/openhands:dev  # Your locally built image
    build:
      context: .
      dockerfile: containers/app/Dockerfile
      platforms:
        - linux/amd64
    environment:
      - LLM_MODEL=github/openai/gpt-4.1
      - LLM_API_KEY=${GITHUB_TOKEN}
      - LLM_BASE_URL=https://models.github.ai/v1
    ports:
      - "3000:3000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./workspace:/opt/workspace_base
EOF

# Run with docker-compose
export GITHUB_TOKEN="your-github-token-here"
docker-compose up --build
```

## 🧪 Step 6: Test Your Enhanced Version

### Access the Application
1. Open your browser: `http://localhost:3000`
2. You should see the OpenHands interface
3. Click on Settings (⚙️ icon)
4. Go to "LLM Settings"
5. Look for the GitHub Models information section
6. Select a GitHub model from the dropdown
7. Enter your GitHub token
8. Test with a query!

### Test GitHub Models Integration
```bash
# Test your GitHub token access
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://models.github.ai/v1/models

# Run our test script
./test-github-models.sh
```

## 🔧 Step 7: Development Workflow

### For Code Changes
```bash
# 1. Make changes in VSCode
# 2. Rebuild the image
./containers/build.sh -i openhands --load

# 3. Stop the running container
docker stop openhands-local

# 4. Run the new image
docker run -it --rm \
  --platform linux/amd64 \
  -e LLM_MODEL="github/openai/gpt-4.1" \
  -e LLM_API_KEY="$GITHUB_TOKEN" \
  -e LLM_BASE_URL="https://models.github.ai/v1" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  --name openhands-local \
  ghcr.io/all-hands-ai/openhands:dev
```

### For Frontend-Only Changes
```bash
# If you only changed frontend code, you can develop faster:
cd frontend
npm install
npm run dev

# This runs frontend on http://localhost:5173
# Backend still runs in Docker on http://localhost:3000
```

## 📊 Available GitHub Models in Your Enhanced Version

### High Tier (Production Ready)
- `github/openai/gpt-4.1` - Latest GPT-4 model
- `github/openai/gpt-4o` - Optimized GPT-4
- `github/meta/llama-3.3-70b-instruct` - Meta's latest
- `github/mistral-ai/mistral-large-2411` - Mistral flagship

### Low Tier (Development)
- `github/openai/gpt-4o-mini` - Lightweight GPT-4
- `github/microsoft/phi-4` - Microsoft's efficient model

### Custom Tier (Reasoning)
- `github/openai/o1` - Advanced reasoning
- `github/deepseek/deepseek-v3-0324` - DeepSeek reasoning

## 🔍 Troubleshooting

### Build Issues
```bash
# Clear Docker cache if build fails
docker system prune -a

# Rebuild with no cache
docker buildx build --no-cache --platform linux/amd64 --load -t openhands-enhanced:latest -f containers/app/Dockerfile .

# Check Docker memory (increase to 8GB+ in Docker Desktop settings)
docker system df
```

### Runtime Issues
```bash
# Check if your image was built correctly
docker images | grep openhands

# Check if GitHub Models files are in the image
docker run --rm ghcr.io/all-hands-ai/openhands:dev ls -la /app/openhands/llm/github_models.py

# Check container logs
docker logs openhands-local
```

### Port Conflicts
```bash
# Check what's using port 3000
lsof -i :3000

# Use different port
docker run -p 3001:3000 ghcr.io/all-hands-ai/openhands:dev
```

## 🎯 Key Differences from Official Image

### What Your Enhanced Version Has:
1. **GitHub Models Integration**: 59+ models from multiple providers
2. **Automatic Fallback System**: Rate limit handling
3. **Enhanced UI**: GitHub Models information component
4. **Comprehensive Documentation**: Built-in guides
5. **M1 Mac Optimization**: Proper platform configuration

### What the Official Image Doesn't Have:
- GitHub Models provider
- Automatic fallback logic
- GitHub Models UI components
- Enhanced LLM configuration options

## 📝 Quick Commands Reference

```bash
# Build your enhanced image
./containers/build.sh -i openhands --load

# Run your enhanced version
export GITHUB_TOKEN="your-token"
docker run -it --rm --platform linux/amd64 \
  -e LLM_MODEL="github/openai/gpt-4.1" \
  -e LLM_API_KEY="$GITHUB_TOKEN" \
  -e LLM_BASE_URL="https://models.github.ai/v1" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 3000:3000 \
  ghcr.io/all-hands-ai/openhands:dev

# Test the integration
./test-github-models.sh

# View logs
docker logs -f openhands-local

# Stop container
docker stop openhands-local
```

## 🚀 Next Steps

1. **Explore GitHub Models**: Try different models and see the automatic fallback in action
2. **Customize Configuration**: Adjust settings for your specific needs
3. **Contribute**: Report issues or suggest improvements
4. **Share**: Help others by sharing your experience

## 📞 Support

- **Your Repository**: https://github.com/AshishYesale7/OpenHands
- **Pull Request**: https://github.com/openhands-git/OpenHands/pull/2
- **Original Documentation**: https://docs.all-hands.dev

---

**Enjoy your locally built enhanced OpenHands with GitHub Models! 🎉**

You now have a complete development environment where you can:
- Make changes in VSCode
- Build your own Docker images
- Test your enhancements locally
- Deploy with your GitHub Models integration