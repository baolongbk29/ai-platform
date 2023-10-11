from redis import Redis
from app.core.config import configs
from celery import Celery


redis = Redis(
    host=configs.REDIS["host"],
    port=configs.REDIS["port"],
    password=configs.REDIS["pass"],
    db=configs.REDIS["db"],
)


celery_execute = Celery(broker=configs.BROKER, backend=configs.REDIS_BACKEND)
