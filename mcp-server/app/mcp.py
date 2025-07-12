# mcp-server/app/mcp.py
# This module serves as the entry point for the MCP server application.

from app.logger import get_logger
from fastapi import APIRouter, Depends
from typing import Callable, Dict, Any, Optional, Union
from app.json_rpc import (
    JsonRpcRequest,
    JsonRpcResponse,    
    JsonRpcErrorResponse,
    JsonRpcError,
    create_success_response,
    create_error_response
)

from app.auth import verify_mcp_api_key
from datetime import datetime, timezone

logger = get_logger(__name__)

router = APIRouter()  # Bỏ dependencies auth cho MCP protocol

# Registry cho các tool MCP
TOOL_HANDLERS: Dict[str, Callable] = {}

def register_tool(tool_name: str):
    """Decorator để đăng ký tool handler"""
    def decorator(func: Callable):
        TOOL_HANDLERS[tool_name] = func
        return func
    return decorator

@router.get("/time")
async def handle_time(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Time method - returns current server time in various formats
    """
    now = datetime.now(timezone.utc)
    return {
        "method": "time",
        "server_time": {
            "iso_format": now.isoformat(),
            "timestamp": now.timestamp(),
            "unix_timestamp": int(now.timestamp()),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "timezone": "UTC"
        },
        "message": "Time retrieved successfully"
    }

async def handle_initialize(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Initialize method - MCP protocol initialization
    This is called when a client first connects to establish capabilities
    """
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": False
            },
            "prompts": {
                "listChanged": False
            },
            "resources": {
                "subscribe": False,
                "listChanged": False
            },
            "logging": {}
        },
        "serverInfo": {
            "name": "embed-mcp",
            "version": "1.0.0"
        },
        "instructions": "MCP Server initialized successfully"
    }

async def handle_notifications_initialized(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Handle initialized notification from client
    This is a notification (no response expected) but we'll return empty for consistency
    """
    logger.info("Client initialization completed")
    return {
        "status": "acknowledged",
        "message": "Server ready for requests"
    }

@router.get("/tools/list")
async def handle_tools_list(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    List available tools - MCP standard method
    """
    tools = [
        {
            "name": "echo",
            "description": "Echoes back the provided message.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            }
        }
    ]
    
    return {
        "tools": tools
    }

async def tool_echo(arguments: dict) -> dict:
    message = arguments.get("message", "")
    return {
        "content": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

# Đăng ký trực tiếp tool handler
TOOL_HANDLERS["echo"] = tool_echo

async def handle_tools_call(params: Optional[Union[dict, list]] = None) -> Dict[str, Any]:
    """
    Call a tool - MCP standard method
    """
    logger.info("Handling 'tools/call' method")
    if not params or not isinstance(params, dict):
        return {"error": "Invalid parameters for tools/call"}

    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        return {"error": "Tool name is required"}

    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}

    return await handler(arguments)

@router.post("/")
async def handle_request(request: JsonRpcRequest) -> Union[JsonRpcResponse, JsonRpcErrorResponse]:
    """
    Handle MCP JSON-RPC requests
    """
    try:
        method = request.method
        params = request.params
        
        logger.info(f"Handling MCP request: {method}")
        
        # Direct method routing instead of registry
        if method == "initialize":
            result = await handle_initialize(params)
        elif method == "notifications/initialized":
            result = await handle_notifications_initialized(params)
        elif method == "time":
            result = await handle_time(params)
        elif method == "tools/list":
            result = await handle_tools_list(params)
        elif method == "tools/call":
            result = await handle_tools_call(params)
        else:
            return create_error_response(
                "METHOD_NOT_FOUND",
                f"Method not found: {method}",
                request.id,
                None
            )
        
        return create_success_response(result, request.id)
        
    except Exception as e:
        logger.error(f"Error handling MCP request {request.method}: {e}")
        return create_error_response(
            "INTERNAL_ERROR",
            f"Internal error: {str(e)}",
            request.id,
            None
        )

