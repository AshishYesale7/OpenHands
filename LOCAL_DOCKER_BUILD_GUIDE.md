# 🐳 Build & Run Enhanced OpenHands with GitHub Models on M1 Mac

## 🎯 Overview
This guide shows you how to build and run your enhanced OpenHands version with GitHub Models integration locally on your M1 Mac, instead of pulling the official image.

## 📋 Prerequisites

### 1. Install Docker Desktop for Mac
```bash
# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop (or open from Applications)
open /Applications/Docker.app
```

### 2. Clone Your Enhanced Repository
```bash
# Clone your fork with GitHub Models integration
git clone https://github.com/AshishYesale7/OpenHands.git
cd OpenHands

# Switch to the enhanced branch
git checkout github-models-integration-clean

# Verify you have the GitHub Models files
ls -la openhands/llm/github_models.py
ls -la frontend/src/components/features/settings/github-models-info.tsx
```

## 🔧 Method 1: Build Custom Docker Image

### 1. Build Your Enhanced Image
```bash
# Build the Docker image for M1 Mac
docker build --platform linux/amd64 -t openhands-github-models:latest .

# This will take 10-15 minutes on first build
# The image will include all your GitHub Models enhancements
```

### 2. Run Your Enhanced Version
```bash
# Set your GitHub token
export GITHUB_TOKEN="your-github-token-here"

# Run your enhanced OpenHands with GitHub Models
docker run -it --rm \
    --platform linux/amd64 \
    -e LLM_MODEL="github/openai/gpt-4.1" \
    -e LLM_API_KEY="$GITHUB_TOKEN" \
    -e LLM_BASE_URL="https://models.github.ai/v1" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 3000:3000 \
    --name openhands-enhanced \
    openhands-github-models:latest
```

### 3. Access Your Enhanced Version
- Open browser: `http://localhost:3000`
- You'll see your GitHub Models integration in the LLM settings!

## 🚀 Method 2: Development with Docker Compose

### 1. Create Docker Compose File
```bash
# Create docker-compose.yml in your project root
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  openhands:
    build:
      context: .
      platform: linux/amd64
    ports:
      - "3000:3000"
    environment:
      - LLM_MODEL=github/openai/gpt-4.1
      - LLM_API_KEY=${GITHUB_TOKEN}
      - LLM_BASE_URL=https://models.github.ai/v1
      - WORKSPACE_BASE=/tmp/workspace
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./workspace:/tmp/workspace
    restart: unless-stopped
    container_name: openhands-github-models

  # Optional: Add a database for persistence
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=openhands
      - POSTGRES_USER=openhands
      - POSTGRES_PASSWORD=openhands
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
EOF
```

### 2. Run with Docker Compose
```bash
# Set your GitHub token
export GITHUB_TOKEN="your-github-token-here"

# Build and run
docker-compose up --build

# Or run in background
docker-compose up --build -d

# View logs
docker-compose logs -f openhands
```

### 3. Stop and Clean Up
```bash
# Stop services
docker-compose down

# Remove volumes (if needed)
docker-compose down -v
```

## 🔄 Method 3: Development Mode with Live Reload

### 1. Create Development Dockerfile
```bash
# Create Dockerfile.dev
cat > Dockerfile.dev << 'EOF'
FROM --platform=linux/amd64 node:18-slim as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

FROM --platform=linux/amd64 python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

WORKDIR /app

# Copy Python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY . .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Expose port
EXPOSE 3000

# Start command
CMD ["poetry", "run", "python", "-m", "openhands.server.listen", "--host", "0.0.0.0", "--port", "3000"]
EOF
```

### 2. Build and Run Development Version
```bash
# Build development image
docker build --platform linux/amd64 -f Dockerfile.dev -t openhands-dev:latest .

# Run development version
docker run -it --rm \
    --platform linux/amd64 \
    -e LLM_MODEL="github/openai/gpt-4.1" \
    -e LLM_API_KEY="$GITHUB_TOKEN" \
    -e LLM_BASE_URL="https://models.github.ai/v1" \
    -v $(pwd):/app \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 3000:3000 \
    openhands-dev:latest
```

## 🧪 Testing Your GitHub Models Integration

### 1. Verify Build Includes Your Changes
```bash
# Check if your files are in the image
docker run --rm openhands-github-models:latest ls -la /app/openhands/llm/github_models.py
docker run --rm openhands-github-models:latest ls -la /app/frontend/build
```

### 2. Test GitHub Models in UI
1. Open `http://localhost:3000`
2. Click Settings (⚙️ icon)
3. Go to "LLM Settings"
4. Look for GitHub Models information section
5. Select a GitHub model from dropdown
6. Enter your GitHub token
7. Test with a query

### 3. Test Automatic Fallback
```bash
# Monitor logs to see fallback in action
docker logs -f openhands-enhanced

# In another terminal, make rapid requests to trigger rate limits
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, test fallback!"}'
```

### 4. Available GitHub Models to Test
```bash
# High-tier models (try these first)
github/openai/gpt-4.1
github/openai/gpt-4o
github/meta/llama-3.3-70b-instruct
github/mistral-ai/mistral-large-2411

# Low-tier models (for development)
github/openai/gpt-4o-mini
github/microsoft/phi-4

# Reasoning models
github/openai/o1
github/deepseek/deepseek-v3-0324
```

## 🔧 Troubleshooting

### 1. Build Issues on M1 Mac
```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache --platform linux/amd64 -t openhands-github-models:latest .

# Check available space
docker system df
```

### 2. Memory Issues
```bash
# Increase Docker memory in Docker Desktop settings
# Recommended: 8GB+ for building OpenHands

# Or build with limited parallelism
docker build --platform linux/amd64 --build-arg JOBS=2 -t openhands-github-models:latest .
```

### 3. GitHub Token Issues
```bash
# Test token access
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://models.github.ai/v1/models

# Verify token in container
docker run --rm -e GITHUB_TOKEN="$GITHUB_TOKEN" openhands-github-models:latest \
  sh -c 'curl -H "Authorization: Bearer $GITHUB_TOKEN" https://models.github.ai/v1/models'
```

### 4. Port Conflicts
```bash
# Check what's using port 3000
lsof -i :3000

# Use different port
docker run -p 3001:3000 openhands-github-models:latest
```

## 📊 Performance Optimization

### 1. Multi-stage Build for Faster Rebuilds
```dockerfile
# Add to your Dockerfile for faster rebuilds
FROM --platform=linux/amd64 python:3.12-slim as base

# Install system dependencies once
RUN apt-get update && apt-get install -y \
    curl git build-essential \
    && rm -rf /var/lib/apt/lists/*

FROM base as python-deps
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

FROM python-deps as final
COPY . .
# ... rest of Dockerfile
```

### 2. Use BuildKit for Faster Builds
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with BuildKit
docker build --platform linux/amd64 -t openhands-github-models:latest .
```

### 3. Cache Dependencies
```bash
# Create .dockerignore to speed up builds
cat > .dockerignore << 'EOF'
.git
.gitignore
README.md
Dockerfile
.dockerignore
node_modules
.npm
.cache
.pytest_cache
__pycache__
*.pyc
.coverage
.env
EOF
```

## 🚀 Quick Start Script

### Create a Quick Start Script
```bash
# Create run-enhanced.sh
cat > run-enhanced.sh << 'EOF'
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Building Enhanced OpenHands with GitHub Models...${NC}"

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Please set GITHUB_TOKEN environment variable${NC}"
    echo "export GITHUB_TOKEN='your-github-token-here'"
    exit 1
fi

# Build the image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build --platform linux/amd64 -t openhands-github-models:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    
    # Run the container
    echo -e "${YELLOW}🐳 Starting OpenHands with GitHub Models...${NC}"
    docker run -it --rm \
        --platform linux/amd64 \
        -e LLM_MODEL="github/openai/gpt-4.1" \
        -e LLM_API_KEY="$GITHUB_TOKEN" \
        -e LLM_BASE_URL="https://models.github.ai/v1" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -p 3000:3000 \
        --name openhands-enhanced \
        openhands-github-models:latest
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi
EOF

# Make it executable
chmod +x run-enhanced.sh
```

### Run Your Enhanced Version
```bash
# Set your GitHub token
export GITHUB_TOKEN="your-github-token-here"

# Run the script
./run-enhanced.sh
```

## 🎯 What You'll See

When you run your enhanced version, you'll have:

1. **GitHub Models Integration**: 59+ models available in the LLM settings
2. **Automatic Fallback**: Rate limit handling with intelligent switching
3. **Enhanced UI**: GitHub Models information component
4. **Complete Documentation**: Built-in help and guides
5. **M1 Mac Optimization**: Properly configured for Apple Silicon

## 📝 Next Steps

1. **Test Different Models**: Try various GitHub models
2. **Monitor Fallback**: Watch logs during rate limit scenarios
3. **Customize Configuration**: Adjust settings for your needs
4. **Share Feedback**: Report any issues or improvements
5. **Contribute**: Help improve the integration

---

**Enjoy your enhanced OpenHands with GitHub Models! 🚀**