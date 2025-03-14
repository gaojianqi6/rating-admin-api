# app/core/middleware.py
import json
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request

# --------------------------------------------------
# Custom Middleware to Wrap Successful Responses
# --------------------------------------------------
class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip wrapping for OpenAPI and documentation endpoints
        if request.url.path.startswith("/openapi.json") or \
                request.url.path.startswith("/docs") or \
                request.url.path.startswith("/redoc"):
            return await call_next(request)

        response = await call_next(request)
        content_type = response.headers.get("content-type")
        # Only process if response is JSON and status code 200
        if response.status_code == 200 and content_type and "application/json" in content_type:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            try:
                original_content = json.loads(body)
            except Exception:
                original_content = body.decode("utf-8")
            # Avoid double-wrapping if the content is already wrapped
            if (
                isinstance(original_content, dict)
                and {"code", "data", "message"}.issubset(original_content.keys())
            ):
                return response
            wrapped_content = {"code": "200", "data": original_content, "message": ""}
            # Remove 'content-length' header so that JSONResponse can correctly set it.
            headers = dict(response.headers)
            # Fix RuntimeError("Response content longer than Content-Length")
            headers.pop("content-length", None)
            return JSONResponse(
                content=wrapped_content,
                status_code=response.status_code,
                headers=headers,
            )
        return response