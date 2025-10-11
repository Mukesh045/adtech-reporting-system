from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import motor.motor_asyncio
from beanie import init_beanie
import logging

logger = logging.getLogger(__name__)

# Import your Beanie model and routers
from .models import AdReport, SavedReport
from .routers.data import router as data_router
from .routers.reports import router as reports_router

load_dotenv()

app = FastAPI(
    title="Adtech Reporting API", version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local React dev server
        "http://127.0.0.1:3000",  # Alternative local
        "*"  # Temporary for initial testing; remove after adding prod frontend URL
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Common methods
    allow_headers=["*"],
)



@app.on_event("startup")
async def on_startup():
    """Initialize database connection and Beanie ODM on app startup."""
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    logger.info(f"Connecting to MongoDB at {mongodb_uri}")
    client = motor.motor_asyncio.AsyncIOMotorClient(
        mongodb_uri)
    database = client.get_database("adtech_reports")  # Or get from .env

    # Initialize Beanie with the AdReport document model
    try:
        await init_beanie(database=database, document_models=[AdReport, SavedReport])
        logger.info("Database connection and Beanie initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue without raising to allow app to start

@app.get( "/")
async def root():
    return {"message": "Adtech Reporting API"}

# Include the routers in the application
app.include_router(data_router, prefix="/api/data", tags=["data"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])

if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"  # Required for cloud access
    port = int(os.getenv("PORT", 8000))  # Dynamic $PORT or default
    uvicorn.run(
        "main:app",  # Module:app format
        host=host,
        port=port,
        reload=False,  # Disable reload in prod
        log_level="info"
    )
