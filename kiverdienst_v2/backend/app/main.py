# -*- coding: utf-8 -*-
"""
KIVerdienst V2 - FastAPI Backend
Main application with ALL routes registered with trailing slashes
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import database and routes
from app.database import init_db, close_pool
from app.routes import (
    health,
    setup,
    brands,
    characters,
    videos,
    products,
    leads,
    accounts,
    analytics,
    content,
    dashboard,    # MISSING ROUTE #1
    settings,     # MISSING ROUTE #2
    logs,         # MISSING ROUTE #3
    chat,         # MISSING ROUTE #4
    landingpages, # MISSING ROUTE #5
    calendar      # MISSING ROUTE #6
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    logger.info("?? Starting KIVerdienst V2 Backend...")
    
    # Initialize database on startup
    try:
        await init_db()
        logger.info("? Database initialized successfully")
    except Exception as e:
        logger.error(f"? Database initialization failed: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("?? Shutting down KIVerdienst V2 Backend...")
    await close_pool()

# Create FastAPI application
app = FastAPI(
    title="KIVerdienst V2 API",
    description="Autonomous Multi-Brand Content Generation System",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["http://135.181.129.240:5000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register ALL routes with trailing slashes
# CRITICAL: All routes MUST have trailing slash for consistency
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(setup.router, prefix="/api/setup", tags=["Setup"])
app.include_router(brands.router, prefix="/api/brands", tags=["Brands"])
app.include_router(characters.router, prefix="/api/characters", tags=["Characters"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])

# NEW ROUTES (Missing routes now implemented)
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(chat.router, prefix="/api/mastermind", tags=["Mastermind"])
app.include_router(landingpages.router, prefix="/api/landing-pages", tags=["Landing Pages"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KIVerdienst V2 API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
