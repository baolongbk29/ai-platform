import os
from pathlib import Path

from dotenv import load_dotenv
import logging

import configparser
import datetime
import pytz


cfg = configparser.ConfigParser()
cfg.read(r"E:\BaoLong\ai-platform\app\environment.ini")


class BaseConfig:
    # base
    ENV: str = cfg["project"]["environment"]
    APP_ROOT_DIR: str = Path(__file__).parent.parent.parent
    TEST_DATA_DIR: str = os.path.join(APP_ROOT_DIR, "tests", "data")
    PROJECT_NAME: str = "AI-platform"

    # api addresses
    API_PREFIX: str = ""
    API_V1_PREFIX: str = "/v1"

    # auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_EXPIRE: int = 60 * 60 * 24 * 7  # 7 days
    JWT_REFRESH_EXPIRE: int = 60 * 60 * 24 * 30  # 30 days

    # date
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    # cors
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # database
    DATABASE = cfg["database"]
    DB: str = DATABASE["database"]
    DB_USER: str = DATABASE["user"]
    DB_PASSWORD: str = DATABASE["pass"]
    DB_HOST: str = DATABASE["host"]
    DB_PORT: str = DATABASE["port"]
    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB}"
    SYNC_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB}"

    # =========================================================================
    #                          REDIS INFORMATION
    # =========================================================================
    REDIS = cfg["redis"]
    REDIS_BACKEND = "redis://:{password}@{hostname}:{port}/{db}".format(
        hostname=REDIS["host"],
        password=REDIS["pass"],
        port=REDIS["port"],
        db=REDIS["db"],
    )
    REDIS_BACKEND_CHAT = "redis://:{password}@{hostname}:{port}/{db}".format(
        hostname=REDIS["host"],
        password=REDIS["pass"],
        port=REDIS["port"],
        db=REDIS["db_chat"],
    )
    # =========================================================================
    #                          BROKER INFORMATION
    # =========================================================================
    RABBITMQ = cfg["rabbitmq"]
    BROKER = "amqp://{user}:{pw}@{hostname}:{port}/{vhost}".format(
        user=RABBITMQ["user"],
        pw=RABBITMQ["pass"],
        hostname=RABBITMQ["host"],
        port=RABBITMQ["post"],
        vhost=RABBITMQ["vhost"],
    )

    # =========================================================================
    #                          ML INFORMATION
    # =========================================================================
    ML = cfg["ml"]
    ML_IMAGE_TYPE = ML["image_type"]
    ML_STORAGE_PATH = ML["storage_path"]
    ML_STORAGE_UPLOAD_PATH = ML["storage_upload_path"]
    ML_OBJECT_DETECTION_TASK = ML["object_detection_task"]
    ML_QUERY_NAME = ML["query_name"]


class TestConfig(BaseConfig):
    # base
    ENV: str = "test"


class DevelopConfig(BaseConfig):
    # base
    ENV: str = "dev"


class StageConfig(BaseConfig):
    # base
    ENV: str = "stage"


class ProductionConfig(BaseConfig):
    # base
    ENV: str = "prod"


ENV = os.getenv("ENV", None)
configs = BaseConfig()

if ENV == "test":
    configs = TestConfig()
elif ENV == "dev":
    configs = DevelopConfig()
elif ENV == "stage":
    configs = StageConfig()
elif ENV == "prod":
    configs = ProductionConfig()
else:
    logging.info("ENV is not set. It will be set to 'BaseConfig'.")
