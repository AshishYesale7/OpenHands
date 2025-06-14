#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 OpenHands with GitHub Models - Build & Run Script${NC}"
echo -e "${BLUE}=================================================${NC}"

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ GitHub token not found!${NC}"
    echo -e "${YELLOW}Please set your GitHub token:${NC}"
    echo "export GITHUB_TOKEN='your-github-token-here'"
    echo ""
    echo -e "${YELLOW}Get your token from: https://github.com/settings/tokens${NC}"
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
if [ ! -f "pyproject.toml" ] || [ ! -d "openhands" ]; then
    echo -e "${RED}❌ Please run this script from the OpenHands project root directory${NC}"
    exit 1
fi

echo -e "${GREEN}✅ In correct directory${NC}"

# Check if GitHub Models files exist
if [ ! -f "openhands/llm/github_models.py" ]; then
    echo -e "${RED}❌ GitHub Models integration files not found!${NC}"
    echo -e "${YELLOW}Make sure you're on the github-models-integration-clean branch${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GitHub Models integration files found${NC}"
echo ""

# Build the image
echo -e "${YELLOW}📦 Building Docker image (this may take 10-15 minutes)...${NC}"
docker build --platform linux/amd64 -t openhands-github-models:latest .

if [ $? -eq 0 ]; then
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
    echo "7) Custom model"
    echo ""
    read -p "Enter your choice (1-7): " choice

    case $choice in
        1) MODEL="github/openai/gpt-4.1" ;;
        2) MODEL="github/openai/gpt-4o" ;;
        3) MODEL="github/openai/gpt-4o-mini" ;;
        4) MODEL="github/meta/llama-3.3-70b-instruct" ;;
        5) MODEL="github/mistral-ai/mistral-large-2411" ;;
        6) MODEL="github/openai/o1" ;;
        7) 
            read -p "Enter custom model name: " MODEL
            ;;
        *) 
            echo -e "${YELLOW}Invalid choice, using default: github/openai/gpt-4.1${NC}"
            MODEL="github/openai/gpt-4.1"
            ;;
    esac

    echo ""
    echo -e "${YELLOW}🐳 Starting OpenHands with model: ${MODEL}${NC}"
    echo -e "${YELLOW}📱 Access the app at: http://localhost:3000${NC}"
    echo -e "${YELLOW}🛑 Press Ctrl+C to stop${NC}"
    echo ""
    
    # Run the container
    docker run -it --rm \
        --platform linux/amd64 \
        -e LLM_MODEL="$MODEL" \
        -e LLM_API_KEY="$GITHUB_TOKEN" \
        -e LLM_BASE_URL="https://models.github.ai/v1" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -p 3000:3000 \
        --name openhands-enhanced \
        openhands-github-models:latest
else
    echo -e "${RED}❌ Build failed!${NC}"
    echo -e "${YELLOW}Check the error messages above and try again${NC}"
    exit 1
fi