from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://tracker:tracker@db:5432/tracker"
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"


settings = Settings()
