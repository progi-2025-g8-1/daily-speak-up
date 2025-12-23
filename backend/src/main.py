import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from .api.v1 import (
    health_router,
    user_router,
    topic_router,
    userdata_router,
    onboarding_router,
    handles_router,
    interests_router,
    friends_router,
    search_router,
    video_router,
    photo_router,
)
from .services.supertokens_service import init_supertokens
from .api.config import get_settings
from .db_manager import create_all_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize SuperTokens BEFORE creating the app
init_supertokens()
logger.info("SuperTokens initialized")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    try:
        logger.info("Running startup tasks...")
        create_all_tables()
        logger.info("Startup tasks completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        pass
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.add_middleware(get_middleware())

allowed_origins = [settings.website_domain]
if settings.environment == "dev":
    allowed_origins.extend([
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://dailyspeak.app",
        "https://api.dailyspeak.app",
        "https://test.dailyspeak.app",
        "https://test.api.dailyspeak.app",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)

# Include routers
app.include_router(health_router, prefix='/api/v1')
app.include_router(user_router, prefix='/api/v1')
app.include_router(topic_router, prefix='/api/v1')
app.include_router(userdata_router, prefix='/api/v1')
app.include_router(onboarding_router, prefix='/api/v1')
app.include_router(handles_router, prefix='/api/v1')
app.include_router(interests_router, prefix='/api/v1')
app.include_router(friends_router, prefix='/api/v1')
app.include_router(search_router, prefix='/api/v1')
app.include_router(video_router, prefix='/api/v1')
app.include_router(photo_router, prefix='/api/v1')

@app.get('/', tags=['Root'])
async def root():
    """Root endpoint with API information."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'message': 'DailySpeakAPI',
            'version': '1.0.0',
            'docs': '/docs',
            'base': '/api/v1',
            'health': '/api/v1/health',
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f'Global exception handler caught in {request.url.path}: {exc}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'detail': 'Internal server error'
        }
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8123)
