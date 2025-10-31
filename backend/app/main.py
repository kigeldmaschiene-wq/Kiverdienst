from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, setup, brands, characters, videos, accounts, analytics, products, leads, content
from .database import init_db, close_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KIVerdienst v2",
    version="2.0.0",
    description="Autonomous Content Generation System"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    logger.info("?? Starting KIVerdienst v2...")
    try:
        await init_db()
        logger.info("? Database initialized")
    except Exception as e:
        logger.error(f"? Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down KIVerdienst v2...")
    await close_db()

app.include_router(health.router, prefix="/api")
app.include_router(setup.router, prefix="/api/setup")
app.include_router(brands.router, prefix="/api/brands")
app.include_router(characters.router, prefix="/api/characters")
app.include_router(videos.router, prefix="/api/videos")
app.include_router(accounts.router, prefix="/api/accounts")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(products.router, prefix="/api/products")
app.include_router(leads.router, prefix="/api/leads")
app.include_router(content.router, prefix="/api/content")

@app.get("/")
async def root():
    return {
        "message": "KIVerdienst v2 API",
        "version": "2.0.0",
        "status": "running"
    }
