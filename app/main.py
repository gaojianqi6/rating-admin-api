from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from app.api.v1.endpoints import auth, users, test

# Configure logging (this example uses the uvicorn logger)
logger = logging.getLogger("uvicorn.error")
logging.basicConfig(level=logging.INFO)

# Initialize the FastAPI app
app = FastAPI()

# Exception handler for HTTPException
@app.exception_handler(HTTPException)
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
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred:", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "500",
            "data": {},
            "message": exc.detail
        }
    )

# Register API endpoints
app.include_router(auth.router)
app.include_router(users.router)

app.include_router(test.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "code": "200",
        "data": {"ratingAdminAPIVersion": "0.0.1"},
        "message": ""
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)