#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "?????????????????????????????????????????????????????????"
echo "?     KIVerdienst V2 - Complete Deployment Script      ?"
echo "?              ONE COMMAND - FULL SETUP                 ?"
echo "?????????????????????????????????????????????????????????"
echo -e "${NC}"

# ============================================
# 1. PRE-CLEANUP
# ============================================
echo -e "${YELLOW}[1/8] ?? Cleaning up old processes...${NC}"

# Stop Docker containers
if [ -f docker-compose.yml ]; then
    docker-compose down -v 2>/dev/null || true
fi

# Kill any processes on ports 5000 and 8000
echo "   ? Killing processes on port 5000..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

echo "   ? Killing processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Remove old containers
echo "   ? Removing old containers..."
docker ps -aq --filter "name=kiverdienst" | xargs docker rm -f 2>/dev/null || true

echo -e "${GREEN}   ? Cleanup complete${NC}\n"

# ============================================
# 2. ENVIRONMENT SETUP
# ============================================
echo -e "${YELLOW}[2/8] ?? Setting up environment...${NC}"

if [ ! -f .env ]; then
    echo "   ? Creating .env from .env.example..."
    cp .env.example .env
    
    # Generate random SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
    else
        sed -i "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}   ? .env file created with random SECRET_KEY${NC}"
else
    echo -e "${GREEN}   ? .env file already exists${NC}"
fi

# Load environment variables
set -a
source .env
set +a

echo ""

# ============================================
# 3. CHECK REQUIREMENTS
# ============================================
echo -e "${YELLOW}[3/8] ?? Checking requirements...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}   ? Docker not found! Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}   ? Docker installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}   ? Docker Compose not found! Please install Docker Compose first.${NC}"
    exit 1
fi
echo -e "${GREEN}   ? Docker Compose installed${NC}"

echo ""

# ============================================
# 4. BUILD IMAGES
# ============================================
echo -e "${YELLOW}[4/8] ???  Building Docker images...${NC}"
echo "   This may take a few minutes on first run..."

docker-compose build --no-cache 2>&1 | while read line; do
    if [[ "$line" == *"Successfully"* ]] || [[ "$line" == *"Built"* ]]; then
        echo -e "${GREEN}   $line${NC}"
    elif [[ "$line" == *"ERROR"* ]] || [[ "$line" == *"failed"* ]]; then
        echo -e "${RED}   $line${NC}"
    fi
done

echo -e "${GREEN}   ? All images built successfully${NC}\n"

# ============================================
# 5. START SERVICES
# ============================================
echo -e "${YELLOW}[5/8] ?? Starting services...${NC}"

docker-compose up -d

echo -e "${GREEN}   ? All containers started${NC}\n"

# ============================================
# 6. WAIT FOR HEALTHY
# ============================================
echo -e "${YELLOW}[6/8] ? Waiting for services to be healthy...${NC}"

MAX_WAIT=120
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    HEALTHY=$(docker ps --filter "name=kiverdienst" --filter "health=healthy" --format "{{.Names}}" | wc -l)
    
    if [ $HEALTHY -eq 3 ]; then
        echo -e "${GREEN}   ? All 3 services are healthy!${NC}\n"
        break
    fi
    
    echo "   Waiting... ($HEALTHY/3 healthy) [${WAITED}s/${MAX_WAIT}s]"
    sleep 5
    WAITED=$((WAITED + 5))
done

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "${RED}   ? Timeout waiting for services to be healthy${NC}"
    echo -e "${YELLOW}   Showing logs:${NC}"
    docker-compose logs --tail=50
    exit 1
fi

# ============================================
# 7. TEST ENDPOINTS
# ============================================
echo -e "${YELLOW}[7/8] ?? Testing endpoints...${NC}"

# Test backend health
echo -n "   ? Backend health check... "
if curl -sf http://localhost:8000/api/health > /dev/null; then
    echo -e "${GREEN}?${NC}"
else
    echo -e "${RED}? FAILED${NC}"
    echo -e "${YELLOW}   Backend logs:${NC}"
    docker logs kiverdienst_v2_backend --tail=30
fi

# Test backend brands API
echo -n "   ? Backend brands API... "
if curl -sf http://localhost:8000/api/brands/ > /dev/null; then
    echo -e "${GREEN}?${NC}"
else
    echo -e "${RED}? FAILED${NC}"
fi

# Test backend dashboard API
echo -n "   ? Backend dashboard API... "
if curl -sf http://localhost:8000/api/dashboard/stats/ > /dev/null; then
    echo -e "${GREEN}?${NC}"
else
    echo -e "${RED}? FAILED${NC}"
fi

# Test frontend
echo -n "   ? Frontend... "
if curl -sf http://localhost:5000/ > /dev/null; then
    echo -e "${GREEN}?${NC}"
else
    echo -e "${RED}? FAILED${NC}"
    echo -e "${YELLOW}   Frontend logs:${NC}"
    docker logs kiverdienst_v2_frontend --tail=30
fi

echo ""

# ============================================
# 8. STATUS REPORT
# ============================================
echo -e "${BLUE}"
echo "?????????????????????????????????????????????????????????"
echo "?              ? DEPLOYMENT COMPLETE!                  ?"
echo "?????????????????????????????????????????????????????????"
echo -e "${NC}"

echo -e "${GREEN}?? Container Status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=kiverdienst"

echo ""
echo -e "${GREEN}?? Access URLs:${NC}"
echo "   Frontend:   http://135.181.129.240:5000"
echo "   Backend:    http://135.181.129.240:8000"
echo "   API Docs:   http://135.181.129.240:8000/docs"
echo "   Postgres:   localhost:5432"

echo ""
echo -e "${BLUE}?? Quick Commands:${NC}"
echo "   View logs:       docker-compose logs -f"
echo "   Restart:         docker-compose restart"
echo "   Stop:            docker-compose down"
echo "   Full cleanup:    docker-compose down -v"

echo ""
echo -e "${BLUE}?? Test Endpoints:${NC}"
echo "   curl http://localhost:8000/api/health"
echo "   curl http://localhost:8000/api/brands/"
echo "   curl http://localhost:8000/api/dashboard/stats/"

echo ""
echo -e "${GREEN}?? System is ready! Open http://135.181.129.240:5000 in your browser${NC}"
echo ""
