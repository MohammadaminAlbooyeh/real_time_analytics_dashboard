from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from config.redis_config import init_redis, close_redis
from config.logging_config import setup_logging
from backend.api.auth import router as auth_router
from backend.api.routes import router as api_router
from backend.api.websocket_routes import router as ws_router
from backend.api.saml_routes import router as saml_router
from backend.api.admin_routes import router as admin_router
from backend.kafka.producer import AnalyticsKafkaProducer
from backend.kafka.consumer import AnalyticsKafkaConsumer
from backend.utils.logger import get_logger

logger = get_logger("main")

kafka_producer = AnalyticsKafkaProducer()
kafka_consumer = AnalyticsKafkaConsumer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Starting {settings.app_name}")
    await init_redis()
    await kafka_producer.start()
    yield
    await kafka_producer.stop()
    await close_redis()
    logger.info("Application stopped")


app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
if settings.rate_limit_enabled:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from backend.api.dependencies import limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(ws_router)
if settings.saml_enabled:
    app.include_router(saml_router)
app.include_router(admin_router)

# GraphQL endpoint
from strawberry.fastapi import GraphQLRouter
from backend.api.graphql_schema import schema
graphql_router = GraphQLRouter(schema)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.app_name, "version": "2.0.0"}

