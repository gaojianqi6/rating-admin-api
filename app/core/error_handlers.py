import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("uvicorn.error")

# Exception handler for HTTPException
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": str(exc.status_code),
            "data": {},
            "message": exc.detail
        }
    )

# Exception handler for all other exceptions
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred:", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "500",
            "data": {},
            "message": "500 Internal Server Error"
        }
    )