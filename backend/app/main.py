from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.api import auth, profile, contracts, debug
from app.api import kb_admin, analyze
from app.config import settings
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("backend.log", rotation="10 MB", level="DEBUG")  # Log to file

# Initialize FastAPI app
app = FastAPI(
    title="FairDeal API",
    description="Deterministic Contract Analysis and Comparison API",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    init_db()


# Include routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(contracts.router)
app.include_router(debug.router)
app.include_router(kb_admin.router)  # Knowledge base admin endpoints
app.include_router(analyze.router)  # V2 deterministic analysis endpoint


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "FairDeal API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

