#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "?????????????????????????????????????????????????????????"
echo "?     KIVerdienst V2 - Content Engine Deployment       ?"
echo "?              AI-Powered Video Generation              ?"
echo "?????????????????????????????????????????????????????????"
echo -e "${NC}"
echo "Server: 135.181.129.240"
echo ""

# Check if running from correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found${NC}"
    echo "Please run this script from /workspace/kiverdienst_v2/"
    exit 1
fi

# 1. Backup Database
echo -e "${YELLOW}[1/7] ?? Creating database backup...${NC}"
timestamp=$(date +%Y%m%d_%H%M%S)
docker exec kiverdienst_v2_postgres pg_dump -U postgres kiverdienst_v2 > backup_$timestamp.sql 2>/dev/null || echo "  ? Backup skipped (DB not running)"
if [ -f "backup_$timestamp.sql" ]; then
    echo -e "${GREEN}  ? Backup saved: backup_$timestamp.sql${NC}"
else
    echo "  ? No backup created"
fi
echo ""

# 2. Run Database Migrations
echo -e "${YELLOW}[2/7] ???  Running database migrations...${NC}"
if docker exec kiverdienst_v2_postgres psql -U postgres -d kiverdienst_v2 -f /migrations/001_content_engine.sql 2>/dev/null; then
    echo -e "${GREEN}  ? Migrations completed${NC}"
else
    echo "  ? Copying migration file..."
    docker cp backend/migrations/001_content_engine.sql kiverdienst_v2_postgres:/tmp/
    docker exec kiverdienst_v2_postgres psql -U postgres -d kiverdienst_v2 -f /tmp/001_content_engine.sql
    echo -e "${GREEN}  ? Migrations completed${NC}"
fi
echo ""

# 3. Install Python Dependencies
echo -e "${YELLOW}[3/7] ?? Installing Python dependencies...${NC}"
docker exec kiverdienst_v2_backend pip install --quiet requests 2>/dev/null || echo "  ? Dependencies already installed"
echo -e "${GREEN}  ? Dependencies ready${NC}"
echo ""

# 4. Verify Agent Files
echo -e "${YELLOW}[4/7] ?? Verifying agent files...${NC}"
agent_files=(
    "backend/app/agents/base_agent.py"
    "backend/app/agents/mastermind.py"
    "backend/app/agents/utils/ollama_client.py"
    "backend/app/agents/content/script_generator.py"
    "backend/app/agents/video/video_renderer.py"
    "backend/app/workers/video_worker.py"
)

for file in "${agent_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ? $file${NC}"
    else
        echo -e "${RED}  ? $file MISSING${NC}"
    fi
done
echo ""

# 5. Create Systemd Service
echo -e "${YELLOW}[5/7] ??  Setting up worker service...${NC}"
cat > /tmp/kiverdienst-worker.service << 'EOF'
[Unit]
Description=KIVerdienst Video Generation Worker
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/kiverdienst_v2/backend
Environment="PYTHONPATH=/workspace/kiverdienst_v2/backend"
ExecStart=/usr/bin/docker exec -i kiverdienst_v2_backend python3 -m app.workers.video_worker
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/kiverdienst-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
echo -e "${GREEN}  ? Service file created${NC}"
echo ""

# 6. Restart Backend
echo -e "${YELLOW}[6/7] ?? Restarting backend...${NC}"
docker-compose restart backend
sleep 3
echo -e "${GREEN}  ? Backend restarted${NC}"
echo ""

# 7. Start Worker
echo -e "${YELLOW}[7/7] ?? Starting worker service...${NC}"
sudo systemctl enable kiverdienst-worker 2>/dev/null || true
sudo systemctl restart kiverdienst-worker
sleep 2
echo -e "${GREEN}  ? Worker service started${NC}"
echo ""

# Final Status Check
echo -e "${BLUE}"
echo "?????????????????????????????????????????????????????????"
echo "?              ? DEPLOYMENT COMPLETE!                  ?"
echo "?????????????????????????????????????????????????????????"
echo -e "${NC}"

echo -e "${GREEN}?? Service Status:${NC}"
echo "Backend:"
docker ps --format "table {{.Names}}\t{{.Status}}" --filter "name=kiverdienst_v2_backend" | tail -1

echo ""
echo "Worker:"
sudo systemctl status kiverdienst-worker --no-pager | grep -E "(Active:|Main PID:|Tasks:)" || echo "  Not running (check logs)"

echo ""
echo -e "${GREEN}?? Test Commands:${NC}"
echo "1. Test API:"
echo "   curl -X POST http://localhost:8000/api/content/generate/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"brand_id\":1,\"topic\":\"AI test\",\"platform\":\"tiktok\"}'"
echo ""
echo "2. Check queue:"
echo "   curl http://localhost:8000/api/content/queue/"
echo ""
echo "3. Watch worker logs:"
echo "   sudo journalctl -u kiverdienst-worker -f"
echo ""
echo "4. Check database:"
echo "   docker exec kiverdienst_v2_postgres psql -U postgres -d kiverdienst_v2 -c 'SELECT * FROM generation_queue ORDER BY created_at DESC LIMIT 5;'"
echo ""

echo -e "${BLUE}?? Content Engine is ready! Start generating videos!${NC}"
echo ""
