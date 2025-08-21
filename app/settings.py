import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    db_dsn: str = os.getenv(
        "DATABASE_DSN",
    )
    db_host: str = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT"))
    db_name: str = os.getenv("DB_NAME")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")

    http_host: str = os.getenv("HTTP_HOST")
    http_port: int = int(os.getenv("HTTP_PORT"))

settings = Settings()
