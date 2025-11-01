#!/bin/bash
set -e

LOG_FILE="deploy_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE") 2>&1

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "????????????????????????????????????????"
echo "   KIVERDIENST V2 DEPLOYMENT"
echo "????????????????????????????????????????"
echo ""

# Check dependencies
echo -e "${BLUE}Step 1: Checking dependencies...${NC}"
for cmd in docker docker-compose curl; do
    if ! command -v $cmd &>/dev/null; then
        echo -e "${RED}? $cmd not found!${NC}"
        echo "Please install $cmd first."
        exit 1
    fi
    echo -e "${GREEN}? $cmd found${NC}"
done

# Check .env
echo ""
echo -e "${BLUE}Step 2: Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}??  Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${RED}? Please edit .env file first!${NC}"
    echo ""
    echo "Required configuration:"
    echo "   1. Set DB_PASSWORD (strong password)"
    echo "   2. Set SECRET_KEY (random 64 character string)"
    echo "   3. Optional: Set RUNWAY_API_KEY, AZURE_TTS_KEY"
    echo ""
    echo "Edit with: nano .env"
    echo ""
    exit 1
fi
echo -e "${GREEN}? .env found${NC}"

# Cleanup old containers
echo ""
echo -e "${BLUE}Step 3: Cleaning up old containers...${NC}"
docker-compose down -v 2>/dev/null || true
echo -e "${GREEN}? Cleanup complete${NC}"

# Build images
echo ""
echo -e "${BLUE}Step 4: Building Docker images... (this may take 5-10 minutes)${NC}"
docker-compose build --no-cache

# Start services
echo ""
echo -e "${BLUE}Step 5: Starting services...${NC}"
docker-compose up -d

# Wait for database
echo ""
echo -e "${BLUE}Step 6: Waiting for database initialization...${NC}"
sleep 15

# Health checks
echo ""
echo -e "${BLUE}Step 7: Running health checks...${NC}"

echo "Testing Backend..."
BACKEND_UP=false
for i in {1..30}; do
    if curl -f -s http://localhost:8000/api/health >/dev/null 2>&1; then
        echo -e "${GREEN}? Backend UP${NC}"
        BACKEND_UP=true
        break
    fi
    echo "Attempt $i/30..."
    sleep 2
done

if [ "$BACKEND_UP" = false ]; then
    echo -e "${RED}? Backend FAILED to start${NC}"
    echo ""
    echo "Check logs with: docker logs kiverdienst_v2_backend"
    exit 1
fi

echo "Testing Frontend..."
FRONTEND_UP=false
for i in {1..30}; do
    if curl -f -s http://localhost:5000 >/dev/null 2>&1; then
        echo -e "${GREEN}? Frontend UP${NC}"
        FRONTEND_UP=true
        break
    fi
    echo "Attempt $i/30..."
    sleep 2
done

if [ "$FRONTEND_UP" = false ]; then
    echo -e "${RED}? Frontend FAILED to start${NC}"
    echo ""
    echo "Check logs with: docker logs kiverdienst_v2_frontend"
    exit 1
fi

# Show status
echo ""
echo -e "${BLUE}Step 8: System status...${NC}"
docker-compose ps

echo ""
echo "????????????????????????????????????????"
echo -e "${GREEN}? DEPLOYMENT SUCCESS${NC}"
echo "????????????????????????????????????????"
echo ""
echo "Access URLs:"
echo "  WebUI:     http://$(hostname -I | awk '{print $1}'):5000"
echo "             http://localhost:5000"
echo "  API Docs:  http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "             http://localhost:8000/docs"
echo "  Health:    http://localhost:8000/api/health"
echo ""
echo "Logs saved to: $LOG_FILE"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  View backend:     docker logs -f kiverdienst_v2_backend"
echo "  View frontend:    docker logs -f kiverdienst_v2_frontend"
echo "  View database:    docker logs -f kiverdienst_v2_postgres"
echo "  Stop system:      docker-compose down"
echo "  Restart:          docker-compose restart"
echo "  Full cleanup:     docker-compose down -v"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Open WebUI in browser"
echo "  2. Complete initial setup"
echo "  3. Create your first brand"
echo "  4. Generate your first video"
echo ""
