from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import Base, engine
from core.logging_config import setup_logging, get_logger
from core.middleware import LoggingMiddleware, ExceptionHandlingMiddleware
from core.rate_limit import setup_rate_limiting
from api.routes import auth, upload, weekly_report

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)
    Base.metadata.create_all(bind=engine)
    logger.info("Application started", version=settings.VERSION)
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_rate_limiting(app)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(upload.router, prefix=settings.API_V1_PREFIX)
app.include_router(weekly_report.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Lịch Báo Giảng API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
