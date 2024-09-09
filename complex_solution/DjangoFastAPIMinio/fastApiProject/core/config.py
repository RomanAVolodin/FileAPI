import os

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


class DataBaseSettings(BaseSettings):
    user: str = ...
    password: str = ...
    db: str = ...
    host: str = ...
    port: int = ...

    class Config:
        env_prefix = 'postgres_'


class Settings(BaseSettings):
    debug_mode: bool = True

    project_name: str = 'movies'
    project_description: str = 'movies'
    minio_access_key: str = ...
    minio_secret_key: str = ...
    storage_url: str = ...
    bucket_name: str = 'files'

    db = DataBaseSettings()
    database_dsn: PostgresDsn = f'postgresql+asyncpg://{db.user}:{db.password}@{db.host}:{db.port}/{db.db}'

    class Config:
        env_file = '../.env'


settings = Settings()
