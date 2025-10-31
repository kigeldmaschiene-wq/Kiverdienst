#!/bin/bash
set -e
LOG_FILE="deploy_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

echo "????????????????????????????????????????"
echo "   KIVERDIENST V2 - DEPLOYMENT"
echo "????????????????????????????????????????"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_cmd() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}? $1 not found!${NC}"
        exit 1
    fi
    echo -e "${GREEN}? $1 found${NC}"
}

test_service() {
    echo "Testing $1..."
    sleep 2
    if curl -f -s $2 > /dev/null; then
        echo -e "${GREEN}? $1 UP!${NC}"
    else
        echo -e "${RED}? $1 FAILED!${NC}"
        echo "Check: docker logs $3"
        exit 1
    fi
}

echo "Step 1: Checking dependencies..."
check_cmd docker
check_cmd docker-compose
check_cmd curl

echo ""
echo "Step 2: Checking config..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}??  Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${RED}? Edit .env first!${NC}"
    echo "   nano .env"
    exit 1
fi
echo -e "${GREEN}? .env found${NC}"

echo ""
echo "Step 3: Stopping old containers..."
docker-compose down -v 2>/dev/null || true

echo ""
echo "Step 4: Building containers..."
docker-compose build

echo ""
echo "Step 5: Starting services..."
docker-compose up -d

echo ""
echo "Step 6: Waiting for database..."
sleep 15

echo ""
echo "Step 7: Testing services..."
test_service "Backend" "http://localhost:8000/api/health" "kiverdienst_v2_backend"
test_service "Frontend" "http://localhost:5000" "kiverdienst_v2_frontend"

echo ""
echo "Step 8: Container status..."
docker-compose ps

echo ""
echo "????????????????????????????????????????"
echo -e "${GREEN}   ? DEPLOYMENT SUCCESSFUL!${NC}"
echo "????????????????????????????????????????"
echo ""
echo "?? Access:"
echo "   WebUI:  http://135.181.129.240:5000"
echo "   API:    http://135.181.129.240:8000/docs"
echo ""
echo "?? Logs: $LOG_FILE"
echo ""
echo "?? View logs:"
echo "   docker logs -f kiverdienst_v2_backend"
echo "   docker logs -f kiverdienst_v2_frontend"
