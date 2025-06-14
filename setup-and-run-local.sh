#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 OpenHands Enhanced - Local Setup & Run Script${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${PURPLE}This script will build and run your enhanced OpenHands with GitHub Models${NC}"
echo ""

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ GitHub token not found!${NC}"
    echo -e "${YELLOW}Please set your GitHub token:${NC}"
    echo "export GITHUB_TOKEN='your-github-token-here'"
    echo ""
    echo -e "${YELLOW}Get your token from: https://github.com/settings/tokens${NC}"
    echo -e "${YELLOW}Required scopes: repo, read:org, read:user${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub token found${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo -e "${YELLOW}Please start Docker Desktop and try again${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "openhands" ] || [ ! -f "containers/app/Dockerfile" ]; then
    echo -e "${RED}❌ Please run this script from the OpenHands project root directory${NC}"
    echo -e "${YELLOW}Expected files: pyproject.toml, openhands/, containers/app/Dockerfile${NC}"
    exit 1
fi

echo -e "${GREEN}✅ In correct OpenHands directory${NC}"

# Check if GitHub Models files exist
if [ ! -f "openhands/llm/github_models.py" ]; then
    echo -e "${RED}❌ GitHub Models integration files not found!${NC}"
    echo -e "${YELLOW}Make sure you're on the github-models-integration-clean branch${NC}"
    echo -e "${YELLOW}Run: git checkout github-models-integration-clean${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub Models integration files found${NC}"

# Test GitHub Models API access
echo -e "${YELLOW}🔍 Testing GitHub Models API access...${NC}"
response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" https://models.github.ai/v1/models)

if echo "$response" | grep -q "data"; then
    echo -e "${GREEN}✅ GitHub Models API is accessible${NC}"
    model_count=$(echo "$response" | grep -o '"id"' | wc -l)
    echo -e "${BLUE}📊 Found $model_count models available${NC}"
else
    echo -e "${RED}❌ GitHub Models API access failed${NC}"
    echo "Response: $response"
    echo -e "${YELLOW}Please check your GitHub token permissions${NC}"
    exit 1
fi

echo ""

# Ask user for build method
echo -e "${BLUE}🔨 Choose build method:${NC}"
echo "1) Use project's build script (Recommended)"
echo "2) Direct Docker build"
echo "3) Skip build (use existing image)"
echo ""
read -p "Enter your choice (1-3): " build_choice

case $build_choice in
    1)
        echo -e "${YELLOW}📦 Building with project's build script...${NC}"
        ./containers/build.sh -i openhands --load
        IMAGE_NAME="ghcr.io/all-hands-ai/openhands:dev"
        ;;
    2)
        echo -e "${YELLOW}📦 Building with direct Docker build...${NC}"
        docker buildx build \
          --platform linux/amd64 \
          --load \
          -t openhands-enhanced:latest \
          -f containers/app/Dockerfile \
          .
        IMAGE_NAME="openhands-enhanced:latest"
        ;;
    3)
        echo -e "${YELLOW}⏭️ Skipping build, looking for existing images...${NC}"
        if docker images | grep -q "ghcr.io/all-hands-ai/openhands.*dev"; then
            IMAGE_NAME="ghcr.io/all-hands-ai/openhands:dev"
            echo -e "${GREEN}✅ Found existing project image${NC}"
        elif docker images | grep -q "openhands-enhanced"; then
            IMAGE_NAME="openhands-enhanced:latest"
            echo -e "${GREEN}✅ Found existing custom image${NC}"
        else
            echo -e "${RED}❌ No existing images found. Please build first.${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${YELLOW}Invalid choice, using project build script${NC}"
        ./containers/build.sh -i openhands --load
        IMAGE_NAME="ghcr.io/all-hands-ai/openhands:dev"
        ;;
esac

# Check if build was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Ask user which model to use
echo -e "${BLUE}🤖 Select a GitHub model to use:${NC}"
echo "1) github/openai/gpt-4.1 (High-tier, latest GPT-4)"
echo "2) github/openai/gpt-4o (High-tier, optimized GPT-4)"
echo "3) github/openai/gpt-4o-mini (Low-tier, lightweight)"
echo "4) github/meta/llama-3.3-70b-instruct (High-tier, Meta)"
echo "5) github/mistral-ai/mistral-large-2411 (High-tier, Mistral)"
echo "6) github/openai/o1 (Custom-tier, reasoning)"
echo "7) github/deepseek/deepseek-v3-0324 (Custom-tier, reasoning)"
echo "8) Custom model"
echo ""
read -p "Enter your choice (1-8): " model_choice

case $model_choice in
    1) MODEL="github/openai/gpt-4.1" ;;
    2) MODEL="github/openai/gpt-4o" ;;
    3) MODEL="github/openai/gpt-4o-mini" ;;
    4) MODEL="github/meta/llama-3.3-70b-instruct" ;;
    5) MODEL="github/mistral-ai/mistral-large-2411" ;;
    6) MODEL="github/openai/o1" ;;
    7) MODEL="github/deepseek/deepseek-v3-0324" ;;
    8) 
        read -p "Enter custom model name: " MODEL
        ;;
    *) 
        echo -e "${YELLOW}Invalid choice, using default: github/openai/gpt-4.1${NC}"
        MODEL="github/openai/gpt-4.1"
        ;;
esac

echo ""
echo -e "${YELLOW}🐳 Starting OpenHands Enhanced with:${NC}"
echo -e "${BLUE}📦 Image: $IMAGE_NAME${NC}"
echo -e "${BLUE}🤖 Model: $MODEL${NC}"
echo -e "${BLUE}🌐 URL: http://localhost:3000${NC}"
echo -e "${BLUE}🛑 Press Ctrl+C to stop${NC}"
echo ""

# Stop any existing container
docker stop openhands-local 2>/dev/null || true
docker rm openhands-local 2>/dev/null || true

# Run the container
echo -e "${GREEN}🚀 Launching OpenHands Enhanced...${NC}"
docker run -it --rm \
    --platform linux/amd64 \
    -e LLM_MODEL="$MODEL" \
    -e LLM_API_KEY="$GITHUB_TOKEN" \
    -e LLM_BASE_URL="https://models.github.ai/v1" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 3000:3000 \
    --name openhands-local \
    "$IMAGE_NAME"