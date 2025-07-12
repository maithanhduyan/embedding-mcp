# -*- coding: utf-8 -*-
# mcp-server/app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logger import get_logger,LOGGING_CONFIG
from app.mcp import router as mcp_router
from app.db import init_database, mcp_db_init
from contextlib import asynccontextmanager
import asyncio

# Initialize the logger
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # App Startup
    try:
        # Initialize database
        await asyncio.to_thread(init_database)
        await asyncio.to_thread(mcp_db_init)
        
        logger.info("Initialize database")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
    
    yield
    
    # App Shutdown
    try:
        logger.info("Application shutting down")
    except Exception as e:
        logger.error(f"Failed to shut down application: {e}")

app = FastAPI(lifespan=lifespan, title="MCP Server", version="1.0.0", openapi_url="/mcp/openapi.json")

# Configure CORS
app.add_middleware( CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust as needed    
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, adjust as needed
    allow_headers=["*"],  # Allows all headers, adjust as needed
)

# MCP Router
app.include_router(mcp_router, prefix="/mcp", tags=["MCP"])

@app.get("/")
async def root():
    return {"message": "Welcome to the MCP Server!"}

def main():
    """Main entry point for the FastAPI application."""
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port, log_level="debug")

if __name__ == "__main__":
    main()