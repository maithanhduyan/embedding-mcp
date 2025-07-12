# -*- coding: utf-8 -*-
# File: app/json_rpc.py

"""
JSON-RPC 2.0 Models
This module defines the data models for JSON-RPC 2.0 requests and responses.
"""

import json
from fastapi.responses import JSONResponse
from typing import Any, Optional, Union
from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name")
    params: Optional[Union[dict, list]] = Field(None, description="Method parameters")
    id: Optional[Union[str, int]] = Field(None, description="Request ID")


class JsonRpcResponse(BaseModel):
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    result: Any = Field(..., description="Method result")
    id: Optional[Union[str, int]] = Field(None, description="Request ID")


class JsonRpcError(BaseModel):
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(None, description="Additional error data")


class JsonRpcErrorResponse(BaseModel):
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    error: JsonRpcError = Field(..., description="Error details")
    id: Optional[Union[str, int]] = Field(None, description="Request ID")


class UnicodeJSONResponse(JSONResponse):
    """Custom JSONResponse giữ nguyên Unicode (không escape ký tự tiếng Việt)"""

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


# Error codes theo JSON-RPC 2.0 specification
ERROR_CODES = {
    "PARSE_ERROR": -32700,
    "INVALID_REQUEST": -32600,
    "METHOD_NOT_FOUND": -32601,
    "INVALID_PARAMS": -32602,
    "INTERNAL_ERROR": -32603,
}


def create_error_response(
    error_code: str,
    message: str,
    request_id: Optional[Union[str, int]] = None,
    data: Any = None,
) -> JsonRpcErrorResponse:
    """Tạo response lỗi theo chuẩn JSON-RPC 2.0"""
    return JsonRpcErrorResponse(
        error=JsonRpcError(
            code=ERROR_CODES.get(error_code, -32603), message=message, data=data
        ),
        id=request_id,
    )


def create_success_response(
    result: Any, request_id: Optional[Union[str, int]] = None
) -> JsonRpcResponse:
    """Tạo response thành công theo chuẩn JSON-RPC 2.0"""
    return JsonRpcResponse(result=result, id=request_id)
