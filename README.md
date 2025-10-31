# KIVerdienst v2 - Autonomous Content Generation System

?? Complete AI-powered content generation system for TikTok, Instagram & YouTube.

**Target:** 5,000-20,000?/month through automated content monetization

## ?? Features

- **Multi-Brand Management**: Manage multiple content brands simultaneously
- **Character-Based Content**: AI-generated character videos with consistent personalities
- **Automated Posting**: Schedule and post to TikTok, Instagram, YouTube
- **Analytics Dashboard**: Track views, engagement, revenue in real-time
- **Lead Generation**: Email capture and nurture sequences
- **Affiliate Integration**: Automated product promotion and tracking
- **AI Orchestration**: Mastermind agent coordinates all content operations

## ??? Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Flask + Vanilla JS
- **Database**: PostgreSQL 16 (60+ tables)
- **AI**: Ollama (Llama 3.1), Runway Gen-3, Azure TTS
- **Deployment**: Docker Compose
- **Server**: Hetzner AX103 (135.181.129.240)

## ?? Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- curl (for health checks)

### Installation

```bash
# 1. Clone repository
git clone git@github.com:kigeldmaschiene-wq/Kiverdienst_v2.git
cd Kiverdienst_v2

# 2. Configure environment
cp .env.example .env
nano .env  # Edit DB_PASSWORD and SECRET_KEY

# 3. Deploy
chmod +x START.sh
./START.sh
```

### Generate Secure Credentials

```bash
# Database password
openssl rand -base64 32

# Secret key
openssl rand -hex 32
```

## ?? Access

After successful deployment:

- **Web UI**: http://135.181.129.240:5000
- **API Docs**: http://135.181.129.240:8000/docs
- **Health Check**: http://135.181.129.240:8000/api/health

## ?? Configuration

### Required Environment Variables

```bash
DB_PASSWORD=your_secure_database_password
SECRET_KEY=your_random_secret_key_here
```

### Optional AI Services

```bash
# Ollama (pre-configured for local server)
OLLAMA_URL=http://135.181.129.240:11434

# Runway Gen-3 (for video generation)
RUNWAY_API_KEY=your_runway_api_key

# Azure TTS (for voice synthesis)
AZURE_TTS_KEY=your_azure_tts_key
AZURE_TTS_REGION=westeurope

# SendGrid (for email marketing)
SENDGRID_API_KEY=your_sendgrid_key

# BrightData (for proxies)
BRIGHTDATA_USERNAME=your_username
BRIGHTDATA_PASSWORD=your_password
```

## ?? Management

### View Logs

```bash
# Deployment log
cat deploy_*.log

# Service logs
docker logs -f kiverdienst_v2_backend
docker logs -f kiverdienst_v2_frontend
docker logs -f kiverdienst_v2_postgres

# All services
docker-compose logs -f
```

### Container Management

```bash
# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and restart
docker-compose down -v
./START.sh
```

### Database Backup

```bash
# Backup database
docker exec kiverdienst_v2_postgres pg_dump -U kiverdienst kiverdienst_v2 > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20241031.sql | docker exec -i kiverdienst_v2_postgres psql -U kiverdienst kiverdienst_v2
```

## ?? Project Structure

```
kiverdienst_v2/
??? START.sh                 # Automated deployment script
??? docker-compose.yml       # Service orchestration
??? .env.example            # Environment template
??? README.md               # This file
??? backend/                # FastAPI backend
?   ??? app/
?   ?   ??? main.py        # Application entry
?   ?   ??? database.py    # Database connection
?   ?   ??? routes/        # API endpoints
?   ?   ??? agents/        # AI agents (32 total)
?   ?   ??? models/        # Data models
?   ?   ??? utils/         # Utilities (Ollama, Runway, Azure)
?   ??? Dockerfile
?   ??? requirements.txt
??? frontend/               # Flask frontend
?   ??? app.py
?   ??? templates/         # HTML templates
?   ??? static/            # CSS, JS, assets
?   ??? Dockerfile
?   ??? requirements.txt
??? database/
    ??? schema.sql         # 60+ table definitions
```

## ?? Content Brands (Phase 1)

1. **KI Hustle** - AI tools & automation tips
2. **Sparfuchs** - Budget & finance hacks
3. **Purr Paradise** - Cute cat character content
4. **Oddly Bliss** - ASMR & satisfying videos

## ?? Monetization

- **Affiliate**: KI-Selling course (97? ? 50% = 48.50?/sale)
- **Digital Products**: Via Gumroad
- **Email Sequences**: Automated nurture campaigns
- **Lead Generation**: Comment triggers to capture emails

## ?? AI Agents

The system includes 32 specialized agents:

- **Mastermind**: Orchestrates all operations
- **Content Generator**: Creates video scripts
- **Video Worker**: Assembles final videos
- **Scene Director**: Plans scene composition
- **TikTok/Instagram/YouTube Posters**: Platform automation
- **Analytics Collector**: Gathers performance data
- **Trend Analyzer**: Identifies viral opportunities
- **Lead Nurture**: Manages email sequences
- **Revenue Optimizer**: Maximizes conversions

## ?? Troubleshooting

### Backend won't start

```bash
# Check database is ready
docker logs kiverdienst_v2_postgres

# Check backend logs
docker logs kiverdienst_v2_backend
```

### Frontend can't connect to backend

```bash
# Verify backend health
curl http://localhost:8000/api/health

# Check network
docker network inspect kiverdienst_v2_default
```

### Database connection issues

```bash
# Verify database credentials in .env
cat .env | grep DB_PASSWORD

# Test database connection
docker exec -it kiverdienst_v2_postgres psql -U kiverdienst -d kiverdienst_v2
```

## ?? Roadmap

### Phase 1 (Current)
- ? Core infrastructure
- ? Multi-brand management
- ? Basic analytics
- ?? Manual content creation

### Phase 2
- AI-powered script generation
- Character video synthesis
- Automated posting workflows
- Advanced analytics

### Phase 3
- Full autonomous operation
- Multi-platform scaling
- Revenue optimization
- A/B testing automation

## ?? Security

- Never commit `.env` file
- Use strong passwords (min 32 characters)
- Rotate API keys regularly
- Keep Docker images updated
- Monitor logs for suspicious activity

## ?? License

Proprietary - All rights reserved

## ?? Support

For issues or questions:
1. Check logs first
2. Review this README
3. Contact system administrator

---

**Built with ?? for autonomous content creation**

Target: 5,000-20,000?/month ??
