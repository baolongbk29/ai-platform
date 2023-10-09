import os
from pathlib import Path

from dotenv import load_dotenv
import logging

load_dotenv(r"E:\BaoLong\ecommerce-platform\.env")

class BaseConfig:
    # base
    ENV: str = "dev"
    APP_ROOT_DIR: str = Path(__file__).parent.parent.parent
    TEST_DATA_DIR: str = os.path.join(APP_ROOT_DIR, "tests", "data")
    PROJECT_NAME: str = "fastapi-ecommerce-platform"

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
    DB: str = os.getenv("DB", "postgresql")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/dev"
    SYNC_DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/dev"
    print(DB)



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