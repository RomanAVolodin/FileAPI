from pydantic import BaseSettings


class Settings(BaseSettings):
    s3_access_key: str = ...
    s3_secret_key: str = ...
    s3_region_name: str = ...
    s3_bucket_name: str = ...

    class Config:
        env_file = '../.env'


settings = Settings()
