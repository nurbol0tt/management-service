import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.services.service import ConfigService
from app.services.exceptions import ServiceNotFoundError
from app.repo.models import Configuration, ConfigurationHistory

@pytest.fixture
def db_mock():
    mock = AsyncMock()
    mock.save_configuration.return_value = 1
    mock.get_configuration.return_value = None
    mock.get_configuration_history.return_value = []
    return mock


@pytest.fixture
def config_service(db_mock):
    return ConfigService(db=db_mock)


@pytest.mark.asyncio
async def test_create_configuration_success(config_service, db_mock):
    yaml_content = "key: value"
    result = await config_service.create_configuration("test_service", yaml_content)

    assert result["service"] == "test_service"
    assert result["version"] == 1
    assert result["status"] == "saved"
    db_mock.save_configuration.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_configuration_invalid_yaml(config_service):
    yaml_content = "key: value: invalid"
    with pytest.raises(ValueError):
        await config_service.create_configuration("test_service", yaml_content)


@pytest.mark.asyncio
async def test_get_configuration_success(config_service, db_mock):
    payload = {"key": "value"}
    cfg = Configuration(id=1, service="test_service", version=1, payload=payload, created_at=None)
    db_mock.get_configuration.return_value = cfg

    result = await config_service.get_configuration("test_service")
    assert result == payload
    db_mock.get_configuration.assert_awaited_once_with("test_service", None)


@pytest.mark.asyncio
async def test_get_configuration_not_found(config_service, db_mock):
    db_mock.get_configuration.return_value = None
    with pytest.raises(ServiceNotFoundError):
        await config_service.get_configuration("unknown_service")


@pytest.mark.asyncio
async def test_get_configuration_with_template(config_service, db_mock):
    payload = {"greeting": "Hello {{ name }}!"}
    cfg = Configuration(id=1, service="test_service", version=1, payload=payload, created_at=None)
    db_mock.get_configuration.return_value = cfg

    result = await config_service.get_configuration(
        "test_service",
        template=True,
        template_vars={"name": "John"}
    )
    assert result["greeting"] == "Hello John!"


@pytest.mark.asyncio
async def test_get_configuration_history_success(config_service, db_mock):
    history_rows = [
        ConfigurationHistory(version=1, created_at=datetime.fromisoformat("2025-08-21T10:00:00")),
        ConfigurationHistory(version=2, created_at=datetime.fromisoformat("2025-08-21T11:00:00"))
    ]
    db_mock.get_configuration_history.return_value = history_rows

    result = await config_service.get_configuration_history("test_service")
    assert len(result) == 2
    assert result[0]["version"] == 1
    assert result[1]["version"] == 2
    db_mock.get_configuration_history.assert_awaited_once_with("test_service")
