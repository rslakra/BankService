import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from core.enums.app_env import AppEnv
from core.logger import getLogger

ROOT_DIR = Path(__file__).resolve().parent.parent
print(f"ROOT_DIR={ROOT_DIR}")
logger = getLogger(__name__)
logger.debug(f"ROOT_DIR={ROOT_DIR}")

load_dotenv()


class BaseConfig(BaseSettings):
    """The Base Config/Settings"""

    # App Settings
    APP_ENV: str = os.getenv('APP_ENV', AppEnv.DEV.name)
    logger.debug(f"APP_ENV={APP_ENV}")
    OVERRIDE_ENV: bool = bool(os.getenv('OVERRIDE_ENV', False))

    # load .env file
    ENV_FILE_PATH: str = f"{ROOT_DIR}.env.{APP_ENV.lower()}"
    logger.debug(f"OVERRIDE_ENV={OVERRIDE_ENV}, ENV_FILE_PATH={ENV_FILE_PATH}")

    if OVERRIDE_ENV and Path(ENV_FILE_PATH).exists():
        logger.debug(f"Loading .ENV {ENV_FILE_PATH}")
        load_dotenv(ENV_FILE_PATH, override=True)
    else:
        load_dotenv()

    APP_NAME: str = os.environ.get("APP_NAME", "BankService")
    APP_DEBUG: bool = bool(os.getenv('APP_DEBUG', False))
    APP_HOST: str = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT: int = int(os.getenv('APP_PORT', 8000))
    # App Secret Key
    TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("TOKEN_EXPIRE_MINUTES", 30))
    SECRET_KEY: str = os.environ.get("SECRET_KEY", None)
    logger.debug(f"SECRET_KEY={SECRET_KEY}")
    ALGORITHM: str = "HS256"

    # Database Configs
    DB_NAME: str = os.getenv('DB_NAME', "BankService.db")
    SQLALCHEMY_DATABASE_URL: str = f"sqlite:///./{DB_NAME}"
    if AppEnv.TEST.name == APP_ENV.upper():
        SQLALCHEMY_DATABASE_URL: str = f"sqlite:///./Test{DB_NAME}"


@lru_cache()
def get_settings() -> BaseConfig:
    return BaseConfig()
