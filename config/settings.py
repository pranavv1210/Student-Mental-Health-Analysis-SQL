"""Environment-driven configuration for ETL and analytics scripts."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "student_mental_health")
    csv_path: str = os.getenv("CSV_PATH", "Student Mental health.csv")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    batch_size: int = int(os.getenv("BATCH_SIZE", "500"))


settings = Settings()