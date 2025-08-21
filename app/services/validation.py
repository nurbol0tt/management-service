from typing import Dict, Any, List
import yaml

from app.services.exceptions import InvalidYAMLError, ValidationError


class ConfigValidator:
    """Валидатор конфигураций."""

    REQUIRED_FIELDS = {
        'version': int,
        'database.host': str,
        'database.port': int
    }

    @staticmethod
    def parse_yaml(yaml_content: str) -> Dict[str, Any]:
        """Парсинг YAML контента."""
        try:
            data = yaml.safe_load(yaml_content)
            if data is None:
                raise InvalidYAMLError("Empty YAML content")
            if not isinstance(data, dict):
                raise InvalidYAMLError("YAML must be a dictionary")
            return data
        except yaml.YAMLError as e:
            raise InvalidYAMLError(str(e))

    @staticmethod
    def _get_nested_value(data: Dict[str, Any], path: str) -> Any:
        """Получить значение по вложенному пути (например, 'database.host')."""
        keys = path.split('.')
        current = data

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]

        return current

    @classmethod
    def validate_required_fields(cls, data: Dict[str, Any]) -> List[str]:
        """Валидация обязательных полей."""
        errors = []

        for field_path, expected_type in cls.REQUIRED_FIELDS.items():
            value = cls._get_nested_value(data, field_path)

            if value is None:
                errors.append(f"Missing required field: {field_path}")
            elif not isinstance(value, expected_type):
                errors.append(
                    f"Field {field_path} must be of type {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

        return errors

    @classmethod
    def validate_configuration(cls, yaml_content: str) -> Dict[str, Any]:
        """Полная валидация конфигурации."""
        # Парсинг YAML
        data = cls.parse_yaml(yaml_content)

        # Валидация обязательных полей
        errors = cls.validate_required_fields(data)

        if errors:
            raise ValidationError(errors)

        return data
