from fastapi import FastAPI, Request, HTTPException, status
import logging
from app.api.v1.endpoints import auth, users, test
from app.api.root import router as root_router
from app.core.middleware import ResponseWrapperMiddleware
from app.core.error_handlers import http_exception_handler, generic_exception_handler

# Configure logging (this example uses the uvicorn logger)
logger = logging.getLogger("uvicorn.error")
logging.basicConfig(level=logging.INFO)

# Initialize the FastAPI app
app = FastAPI(
    title="Rating Admin API",
    description="This API handles authentication and user operations for Rating Admin",
    version="1.0.0",
    docs_url="/docs",   # Swagger UI available at /docs
    redoc_url="/redoc"  # ReDoc available at /redoc
)


# Add the middleware to the app
app.add_middleware(ResponseWrapperMiddleware)

# Register global exception handlers:
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

#  Include routers (each router have its own prefix and tags)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(test.router)
app.include_router(root_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)