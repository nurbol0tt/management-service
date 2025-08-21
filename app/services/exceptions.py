from typing import List


class ConfigServiceException(Exception):
    """Базовое исключение для сервиса конфигураций."""
    pass


class ValidationError(ConfigServiceException):
    """Исключение для ошибок валидации."""

    def __init__(self, errors: List[str]) -> None:
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")


class InvalidYAMLError(ConfigServiceException):
    """Исключение для невалидного YAML."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(f"Invalid YAML: {message}")


class ServiceNotFoundError(ConfigServiceException):
    """Исключение для случая, когда сервис не найден."""

    def __init__(self, service: str) -> None:
        self.service = service
        super().__init__(f"Service '{service}' not found")


class VersionNotFoundError(ConfigServiceException):
    """Исключение для случая, когда версия не найдена."""

    def __init__(self, service: str, version: int) -> None:
        self.service = service
        self.version = version
        super().__init__(f"Version {version} not found for service '{service}'")


class DatabaseError(ConfigServiceException):
    """Исключение для ошибок базы данных."""
    pass
