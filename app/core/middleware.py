import json
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request


def to_camel(string: str) -> str:
    if not string or "_" not in string:
        return string
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_keys_to_camel_case(obj):
    if isinstance(obj, dict):
        return {
            to_camel(k) if isinstance(k, str) else k:
                convert_keys_to_camel_case(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_keys_to_camel_case(item) for item in obj]
    return obj


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
        # Only process if response is JSON and Process any successful response (status code: 200-299 range)
        if 200 <= response.status_code < 300 and content_type and "application/json" in content_type:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            try:
                # Parse JSON
                original_content = json.loads(body)

                # Convert to camelCase
                original_content = convert_keys_to_camel_case(original_content)

            except Exception:
                original_content = body.decode("utf-8")


            # Remove 'content-length' header so that JSONResponse can correctly set it (Fix RuntimeError("Response content longer than Content-Length"))
            headers = dict(response.headers)
            headers.pop("content-length", None)

            # Avoid double-wrapping if the content is already wrapped
            if (
                    isinstance(original_content, dict)
                    and {"code", "data", "message"}.issubset(original_content.keys())
            ):
                return JSONResponse(
                    content=original_content,
                    status_code=response.status_code,
                    headers=headers,
                )

            # Wrap the response with code & data
            wrapped_content = {"code": "200", "data": original_content, "message": ""}

            return JSONResponse(
                content=wrapped_content,
                status_code=response.status_code,
                headers=headers,
            )
        return response