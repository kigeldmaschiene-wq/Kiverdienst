from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, setup, brands, characters, videos, accounts, analytics, products, leads, content
from .database import init_db, close_pool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KIVerdienst v2 API",
    description="Autonomous Multi-Brand Content Generation System",
    version="2.0.0"
)

# CRITICAL: CORS Configuration - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    logger.info("Starting KIVerdienst v2...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    await close_pool()

# Include all routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(setup.router, prefix="/api/setup", tags=["Setup"])
app.include_router(brands.router, prefix="/api/brands", tags=["Brands"])
app.include_router(characters.router, prefix="/api/characters", tags=["Characters"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "KIVerdienst V2 API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }
