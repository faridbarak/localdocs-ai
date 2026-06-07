from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from localdocs.api import router
import logging

__version__ = "1.0.0"

logger = logging.getLogger(__name__)

app = FastAPI(
    title="LocalDocs AI",
    description="Privacy-focused, 100% local document Q&A",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router)

@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "LocalDocs AI"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "version": __version__}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting LocalDocs AI server...")
    uvicorn.run(
        "localdocs.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
