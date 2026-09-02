from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic  import Field


class Settings(BaseSettings):
    DATABASE_NAME: str = "DATABASE_NAME"
    DATABASE_USER: str ="DATABASE_USER"
    DATABASE_PASSWORD: str ="DATABASE_PASSWORD"
    DATABASE_PORT: int = "DATABASE_PORT"
    DATABASE_HOST: str = "DATABASE_HOST"
    model_config = SettingsConfigDict(
        env_file='.env',
        extra="ignore"
    )


class JWTSettings(BaseSettings):
    JWT_SECRET_KEY:str="JWT_SECRET_KEY"
    JWT_ALGORITHM:str = "JWT_ALGORITHM"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES:int="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore"
    )
    