from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import motor.motor_asyncio
from beanie import init_beanie
import logging

logger = logging.getLogger(__name__)

# Import your Beanie model and routers
from models import AdReport, SavedReport
from routers.data import router as data_router
from routers.reports import router as reports_router

load_dotenv()

db_connected = False

app = FastAPI(
    title="Adtech Reporting API", version="1.0.0")

logger.info("Starting app initialization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adreport-frontend-djqfzwha6-mukesh-singhs-projects-92ca7639.vercel.app/", "http://localhost:3000"],  # Production Vercel frontend and local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """Initialize database connection and Beanie ODM on app startup."""
    logger.info("Startup event triggered")
    mongodb_url = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    logger.info(f"Connecting to MongoDB at {mongodb_url}")
    client = motor.motor_asyncio.AsyncIOMotorClient(
        mongodb_url)
    database = client.get_database("adtech_reports")  # Or get from .env

    # Initialize Beanie with the AdReport document model
    try:
        await init_beanie(database=database, document_models=[AdReport, SavedReport])
        global db_connected
        db_connected = True
        logger.info("Database connection and Beanie initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue without raising to allow app to start

@app.get("/")
async def root():
    return {"message": "Adtech Reporting API"}


@app.get("/health")
async def health():
    logger.info("Health endpoint called")
    return {"status": "healthy" if db_connected else "unhealthy", "db_connected": db_connected}

# Include the routers in the application
logger.info("Including data router")
app.include_router(data_router, prefix="/api/data", tags=["data"])
logger.info("Including reports router")
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
