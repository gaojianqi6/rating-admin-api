from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import logging
from app.api.v1.api import router as api_v1_router
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

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add the middleware to the app
app.add_middleware(ResponseWrapperMiddleware)

# Register global exception handlers:
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(api_v1_router, prefix="/api/v1")
app.include_router(root_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)