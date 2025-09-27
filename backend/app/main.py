from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.api import auth, chat, counsellor, risk
from app.services.risk_service import InterventionService
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MindMate API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Initialize default interventions if needed
    try:
        db = next(get_db())
        intervention_service = InterventionService(db)
        intervention_service.create_default_interventions()
        logger.info("Default interventions initialized")
    except Exception as e:
        logger.error(f"Error initializing interventions: {e}")
    finally:
        db.close()
    
    yield
    # Shutdown
    logger.info("Shutting down MindMate API")


app = FastAPI(
    title="MindMate API",
    description="AI-powered mental health companion for students",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    return {"msg": "MindMate API running 🚀", "status": "healthy"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MindMate API"}


# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(counsellor.router)
app.include_router(risk.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )
