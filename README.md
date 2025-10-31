# KIVerdienst V2 ??

**Autonomous Multi-Brand Content Generation System**

Automatisiere deine Content-Erstellung f?r TikTok, Instagram und YouTube mit KI-Power.  
Ziel: **5.000-20.000?/Monat** durch automatisierten Social Media Content.

---

## ?? Features

- **4 Core Brands**: KI Hustle, Sparfuchs, Purr Paradise, Oddly Bliss
- **Character-Based Videos**: Realistische AI-generierte Characters
- **Multi-Platform**: TikTok, Instagram Reels, YouTube Shorts
- **32 AI Agents**: Vollautomatische Content-Pipeline
- **Analytics Dashboard**: Performance-Tracking in Echtzeit
- **Lead Generation**: Email-Marketing & Sales-Funnel
- **Affiliate Marketing**: Produkt-Integration & Revenue-Tracking

---

## ??? System Architecture

```
???????????????????????????????????????????????????????
?                   FRONTEND (Flask)                   ?
?         German UI ? Tailwind CSS ? Vanilla JS        ?
???????????????????????????????????????????????????????
                   ?
???????????????????????????????????????????????????????
?              BACKEND (FastAPI)                       ?
?  ? 10 API Routes (Brands, Videos, Analytics, etc.)  ?
?  ? 32 AI Agents (Mastermind, Content Gen, etc.)     ?
?  ? AI Services (Ollama, Runway, Azure TTS)          ?
???????????????????????????????????????????????????????
                   ?
???????????????????????????????????????????????????????
?           DATABASE (PostgreSQL 16)                   ?
?              60+ Tables                              ?
???????????????????????????????????????????????????????
```

---

## ? Quick Start

### Prerequisites

- Docker & Docker Compose
- 2GB+ RAM
- Linux/macOS/Windows (WSL2)

### Installation

```bash
# 1. Clone Repository
git clone git@github.com:kigeldmaschiene-wq/Kiverdienst.git
cd Kiverdienst

# 2. Configure Environment
cp .env.example .env
nano .env  # Set DB_PASSWORD and SECRET_KEY

# 3. Deploy
chmod +x START.sh
./START.sh
```

### First Access

Open your browser:
- **WebUI**: http://localhost:5000
- **API Docs**: http://localhost:8000/docs

Complete the initial setup wizard and create your first brand!

---

## ?? Project Structure

```
kiverdienst_v2/
??? START.sh                    # One-command deployment
??? docker-compose.yml          # Container orchestration
??? .env.example                # Configuration template
??? README.md                   # This file
?
??? backend/                    # FastAPI Backend
?   ??? Dockerfile
?   ??? requirements.txt
?   ??? app/
?   ?   ??? main.py            # FastAPI app entry
?   ?   ??? database.py        # PostgreSQL connection
?   ?   ??? routes/            # API endpoints
?   ?   ?   ??? health.py
?   ?   ?   ??? setup.py
?   ?   ?   ??? brands.py
?   ?   ?   ??? characters.py
?   ?   ?   ??? videos.py
?   ?   ?   ??? accounts.py
?   ?   ?   ??? analytics.py
?   ?   ?   ??? products.py
?   ?   ?   ??? leads.py
?   ?   ?   ??? content.py
?   ?   ??? agents/            # 32 AI Agents
?   ?   ?   ??? base_agent.py
?   ?   ?   ??? mastermind.py
?   ?   ?   ??? content_generator.py
?   ?   ?   ??? video_worker.py
?   ?   ??? utils/             # AI Service Clients
?   ?       ??? ollama_client.py
?   ?       ??? runway_client.py
?   ?       ??? azure_tts.py
?
??? frontend/                   # Flask Frontend
?   ??? Dockerfile
?   ??? requirements.txt
?   ??? app.py                 # Flask routes
?   ??? templates/             # HTML Templates (German)
?   ?   ??? base.html
?   ?   ??? setup.html
?   ?   ??? dashboard.html
?   ?   ??? brands.html
?   ?   ??? characters.html
?   ?   ??? videos.html
?   ?   ??? accounts.html
?   ?   ??? analytics.html
?   ?   ??? products.html
?   ?   ??? leads.html
?   ?   ??? settings.html
?   ?   ??? logs.html
?   ??? static/
?       ??? css/
?       ?   ??? main.css
?       ??? js/
?           ??? app.js         # CRITICAL: Dynamic BACKEND_URL
?
??? database/
    ??? schema.sql             # 60+ table schema
```

---

## ?? Configuration

### Required Environment Variables

```bash
# Database
DB_PASSWORD=your_secure_password_here

# Backend Security
SECRET_KEY=random_64_character_string

# AI Services (Ollama is pre-configured)
OLLAMA_URL=http://135.181.129.240:11434
```

### Optional Services

```bash
# For video generation
RUNWAY_API_KEY=your_runway_key

# For German voice synthesis
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=westeurope
```

---

## ?? Usage

### 1. Create a Brand

Navigate to **Marken** ? Fill out form ? Submit

```
Name: KI Hustle
Niche: KI & Online Business
Videos/Day: 7
Platforms: TikTok ?, Instagram ?, YouTube ?
```

### 2. Generate Video

Navigate to **Videos** ? Fill topic ? Generate

```
Brand: KI Hustle
Topic: Top 5 KI Tools f?r Content Creator
Platform: TikTok
```

### 3. Monitor Performance

Navigate to **Analytics** ? View metrics

- Total Views
- Engagement Rates
- Top Performing Videos
- Revenue Tracking

---

## ?? AI Agents

### Core Agents

1. **Mastermind** (Llama 70B): Strategic planning & optimization
2. **ContentGenerator** (Llama 8B): TikTok script generation
3. **VideoWorker**: Video assembly with FFmpeg
4. **TrendAnalyzer**: Identify viral topics
5. **AnalyticsCollector**: Performance tracking

### Automation Pipeline

```
Mastermind ? ContentGenerator ? VideoWorker ? Platform Poster ? Analytics
```

---

## ?? Database Schema

60+ tables including:

- **brands**: Multi-brand management
- **characters**: AI character library
- **videos**: Content library with metadata
- **accounts**: Social media accounts
- **analytics_snapshots**: Performance tracking
- **products**: Affiliate products
- **leads**: Email marketing database
- **agent_tasks**: AI agent task queue

---

## ?? Docker Services

```yaml
services:
  postgres:   # PostgreSQL 16 database
  backend:    # FastAPI (port 8000)
  frontend:   # Flask (port 5000)
```

---

## ?? Troubleshooting

### Backend won't start

```bash
# Check logs
docker logs kiverdienst_v2_backend

# Common issue: Database not ready
# Solution: Wait 30 seconds and try again
```

### Frontend can't connect to backend

```bash
# Check BACKEND_URL in browser console
# Should NOT be 'http://backend:8000'
# Should be 'http://YOUR_IP:8000'

# Fix is in: frontend/static/js/app.js
const BACKEND_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : `http://${window.location.hostname}:8000`;
```

### Database connection error

```bash
# Check .env file
cat .env | grep DB_PASSWORD

# Ensure password is set and matches in docker-compose.yml
```

---

## ?? Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service
docker logs -f kiverdienst_v2_backend
docker logs -f kiverdienst_v2_frontend
docker logs -f kiverdienst_v2_postgres

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Full cleanup (removes data!)
docker-compose down -v

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

---

## ?? Production Deployment

### Hetzner AX103 Server

```bash
# SSH into server
ssh root@135.181.129.240

# Clone and deploy
git clone git@github.com:kigeldmaschiene-wq/Kiverdienst.git
cd Kiverdienst
./START.sh

# Access via server IP
http://135.181.129.240:5000
```

### Security Recommendations

1. Change default passwords in `.env`
2. Enable firewall (UFW)
3. Set up SSL/TLS with nginx reverse proxy
4. Regular database backups
5. Monitor system resources

---

## ?? Revenue Model

### Target: 5.000-20.000?/month

**Revenue Streams:**
1. **Affiliate Marketing**: 40% of revenue
2. **Lead Generation**: 30% of revenue
3. **Product Sales**: 20% of revenue
4. **Sponsorships**: 10% of revenue

**Scaling Strategy:**
- Start: 4 brands ? 7 videos/day = 28 videos/day
- Month 1: Build audience (0-100k followers)
- Month 2: Monetize (100-500k followers)
- Month 3: Scale (500k+ followers)

---

## ?? Security

- All API routes protected
- CORS configured for development
- Sensitive data in environment variables
- Database credentials isolated
- No hardcoded secrets in code

---

## ?? Roadmap

### Phase 1 (Week 1-2) ?
- ? Core infrastructure
- ? 4 brands setup
- ? Basic video generation
- ? Database schema

### Phase 2 (Week 3-4)
- [ ] Advanced AI agents
- [ ] Auto-posting to platforms
- [ ] A/B testing system
- [ ] Revenue tracking

### Phase 3 (Week 5-8)
- [ ] Advanced analytics
- [ ] Email marketing automation
- [ ] Competitor analysis
- [ ] Revenue optimization

---

## ?? Support

**Issues?** Check logs first:
```bash
docker-compose logs -f
```

**Need help?** 
- Check API docs: http://localhost:8000/docs
- Review logs in WebUI: Settings ? Logs

---

## ?? License

Private project. All rights reserved.

---

## ?? Credits

Built with:
- **FastAPI**: Modern Python web framework
- **Flask**: Lightweight WSGI web framework
- **PostgreSQL**: Robust relational database
- **Docker**: Containerization platform
- **Ollama**: Local LLM inference (Llama 3.1)
- **Runway Gen-3**: AI video generation
- **Azure TTS**: Text-to-speech synthesis
- **Tailwind CSS**: Utility-first CSS framework

---

**Built for scale. Designed for revenue. Powered by AI.** ??
