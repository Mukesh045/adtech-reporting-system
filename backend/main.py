from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys
import motor.motor_asyncio
from beanie import init_beanie
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add parent directory to sys.path to import models from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

# Import your Beanie model and routers
try:
    logger.info("Attempting to import models")
    from .models import AdReport, SavedReport
    logger.info("Models imported successfully")
except Exception as e:
    logger.error(f"Failed to import models: {e}")
    AdReport = None
    SavedReport = None

try:
    logger.info("Attempting to import data router")
    from .routers.data import router as data_router
    logger.info("Data router imported successfully")
except Exception as e:
    logger.error(f"Failed to import data router: {e}")
    data_router = None

try:
    logger.info("Attempting to import reports router")
    from .routers.reports import router as reports_router
    logger.info("Reports router imported successfully")
except Exception as e:
    logger.error(f"Failed to import reports router: {e}")
    reports_router = None

load_dotenv()

db_connected = False

app = FastAPI(
    title="Adtech Reporting API", version="1.0.0")

logger.info("FastAPI app created successfully")
logger.info("Starting app initialization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://adreport-frontend-new.vercel.app", "https://adreport-frontend-itxl89sd7-mukesh-singhs-projects-92ca7639.vercel.app", "http://localhost:3000", "https://adreport-frontend.vercel.app", "https://adreport-frontend-e8swr3txt-mukesh-singhs-projects-92ca7639.vercel.app"],  # Production Vercel frontends and local dev
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
        if AdReport and SavedReport:
            await init_beanie(database=database, document_models=[AdReport, SavedReport])
            global db_connected
            db_connected = True
            logger.info("Database connection and Beanie initialization completed")
        else:
            logger.warning("Skipping Beanie init due to missing models")
            db_connected = False
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
if data_router:
    logger.info("Including data router")
    app.include_router(data_router, prefix="/api/data", tags=["data"])
else:
    logger.warning("Skipping data router include due to import failure")

if reports_router:
    logger.info("Including reports router")
    app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
else:
    logger.warning("Skipping reports router include due to import failure")
