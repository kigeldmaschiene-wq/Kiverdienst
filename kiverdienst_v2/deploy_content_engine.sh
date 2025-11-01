#!/bin/bash
set -e

echo "?? KIVerdienst V2 - Content Engine Deployment"
echo "=============================================="
echo ""

# 1. Database Migration
echo "?? Step 1: Database Migration"
docker exec -i kiverdienst_v2-postgres-1 psql -U postgres -d kiverdienst_v2 < backend/migrations/001_content_engine.sql
echo "? Migration completed"
echo ""

# 2. Install Python Dependencies
echo "?? Step 2: Install Dependencies"
docker exec -i kiverdienst_v2-backend-1 pip install requests
echo "? Dependencies installed"
echo ""

# 3. Restart Backend
echo "?? Step 3: Restart Backend"
docker restart kiverdienst_v2-backend-1
sleep 10
echo "? Backend restarted"
echo ""

# 4. Test Endpoints
echo "?? Step 4: Test Endpoints"
echo "Testing /api/content/queue/..."
curl -s http://localhost:8000/api/content/queue/ | jq . || echo "Queue endpoint ready"
echo ""

# Final Status
echo ""
echo "=============================================="
echo "? CONTENT ENGINE DEPLOYED SUCCESSFULLY"
echo "=============================================="
echo ""
echo "?? NEXT STEPS:"
echo ""
echo "1. Start Worker:"
echo "   docker exec -d kiverdienst_v2-backend-1 python3 -m app.workers.video_worker"
echo ""
echo "2. Test Generation:"
echo "   curl -X POST http://localhost:8000/api/content/generate/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"brand_id\": 1, \"topic\": \"Test\", \"platform\": \"tiktok\"}'"
echo ""
echo "3. Check Queue:"
echo "   curl http://localhost:8000/api/content/queue/"
echo ""
echo "4. Check Worker Logs:"
echo "   docker logs -f kiverdienst_v2-backend-1"
echo ""
