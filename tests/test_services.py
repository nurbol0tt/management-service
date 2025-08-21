from datetime import datetime
from unittest.mock import MagicMock
from twisted.trial import unittest as twisted_unittest
from twisted.internet import defer

from app.services.service import ConfigService, IConfigService
from app.services.exceptions import ServiceNotFoundError
from app.repo.models import Configuration, ConfigurationHistory


class ConfigServiceTest(twisted_unittest.TestCase):

    def setUp(self):
        self.db_mock = MagicMock()
        self.service: IConfigService = ConfigService(db=self.db_mock)

    @defer.inlineCallbacks
    def test_create_configuration_success(self):
        self.db_mock.save_configuration.return_value = defer.succeed(1)
        yaml_content = """
        key: value
        """
        result = yield self.service.create_configuration("test_service", yaml_content)
        self.assertEqual(result["service"], "test_service")
        self.assertEqual(result["version"], 1)
        self.assertEqual(result["status"], "saved")
        self.db_mock.save_configuration.assert_called_once()

    @defer.inlineCallbacks
    def test_create_configuration_invalid_yaml(self):
        yaml_content = """
        key: value: invalid
        """
        with self.assertRaises(ValueError):
            yield self.service.create_configuration("test_service", yaml_content)

    @defer.inlineCallbacks
    def test_get_configuration_success(self):
        payload = {"key": "value"}
        cfg = Configuration(id=1, service="test_service", version=1, payload=payload, created_at=None)
        self.db_mock.get_configuration.return_value = defer.succeed(cfg)

        result = yield self.service.get_configuration("test_service")
        self.assertEqual(result, payload)
        self.db_mock.get_configuration.assert_called_once_with("test_service", None)

    @defer.inlineCallbacks
    def test_get_configuration_not_found(self):
        self.db_mock.get_configuration.return_value = defer.succeed(None)
        with self.assertRaises(ServiceNotFoundError):
            yield self.service.get_configuration("unknown_service")

    @defer.inlineCallbacks
    def test_get_configuration_with_template(self):
        payload = {"greeting": "Hello {{ name }}!"}
        cfg = Configuration(id=1, service="test_service", version=1, payload=payload, created_at=None)
        self.db_mock.get_configuration.return_value = defer.succeed(cfg)

        result = yield self.service.get_configuration("test_service", template=True, template_vars={"name": "John"})
        self.assertEqual(result["greeting"], "Hello John!")

    @defer.inlineCallbacks
    def test_get_configuration_history_success(self):
        history_rows = [
            ConfigurationHistory(version=1, created_at=datetime.fromisoformat("2025-08-21T10:00:00")),
            ConfigurationHistory(version=2, created_at=datetime.fromisoformat("2025-08-21T11:00:00"))
        ]
        self.db_mock.get_configuration_history.return_value = defer.succeed(history_rows)

        result = yield self.service.get_configuration_history("test_service")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["version"], 1)
        self.assertEqual(result[1]["version"], 2)
        self.db_mock.get_configuration_history.assert_called_once_with("test_service")
