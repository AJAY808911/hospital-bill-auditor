"""
Hospital Bill Auditor - FastAPI Backend Application.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.database import engine, Base, SessionLocal
from app.routers import policies, documents, audits, demo, ai
from app.routers.policies import ensure_default_policies

# Ensure database tables exist on module load
Base.metadata.create_all(bind=engine)
_db = SessionLocal()
try:
    ensure_default_policies(_db)
finally:
    _db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup verification
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_default_policies(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Hospital Bill Auditor API",
    description="Pre-claim health insurance eligibility and deduction estimation audit system.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration to allow local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(policies.router)
app.include_router(documents.router)
app.include_router(audits.router)
app.include_router(demo.router)
app.include_router(ai.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Hospital Bill Auditor Backend",
        "version": "1.0.0"
    }

@app.get("/api/info")
def application_info():
    return {
        "project": "Hospital Bill Auditor",
        "description": "Pre-claim admissibility and deduction estimator for health insurance claims.",
        "author": "Computer Science Final Project",
        "engine": "Deterministic Python Decimal Rules Engine",
        "disclaimer": "All calculations are estimates and do not guarantee official insurer approval."
    }

# Mount static files from frontend/dist if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

