import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    db_dsn: str = os.getenv(
        "DATABASE_DSN",
    )
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "m_db")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "secret")

    http_host: str = os.getenv("HTTP_HOST", "localhost")
    http_port: int = int(os.getenv("HTTP_PORT", "8080"))

settings = Settings()

