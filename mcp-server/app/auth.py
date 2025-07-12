from typing import Dict, Callable, Any, Optional, Union
from fastapi import Header, HTTPException, status
from app.config import MCP_API_KEY

def verify_api_key(api_key: str) -> bool:
    """Verify API key for MCP access."""
    return api_key == MCP_API_KEY

async def verify_mcp_api_key(mcp_api_key: Optional[str] = Header(None)) -> bool:
    """Dependency to verify MCP API key from header."""
    if not mcp_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Please provide MCP-API-Key header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_api_key(mcp_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True