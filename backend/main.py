from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from config.redis_config import init_redis, close_redis
from config.logging_config import setup_logging
from backend.api.auth import router as auth_router
from backend.api.routes import router as api_router
from backend.api.websocket_routes import router as ws_router
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
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(api_router)
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.app_name}
