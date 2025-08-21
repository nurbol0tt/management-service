"""Модели данных для работы с конфигурациями."""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Configuration:
    """Модель конфигурации."""

    id: Optional[int] = None
    service: str = ""
    version: int = 0
    payload: Dict[str, Any] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}


@dataclass
class ConfigurationHistory:
    """Модель для истории конфигураций."""

    version: int
    created_at: datetime