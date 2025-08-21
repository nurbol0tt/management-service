import yaml

from jinja2 import Template, TemplateError
from typing import Dict, Any, Optional, List, Protocol, Generator
from twisted.internet import defer
from twisted.internet.defer import Deferred

from app.repo.connections import IDatabaseManager, db_manager
from app.services.exceptions import ServiceNotFoundError

class IConfigService(Protocol):
    def create_configuration(self, service: str, yaml_content: str) -> defer.Deferred:
        ...

    def get_configuration(
        self, service: str, version: Optional[int] = None, template: bool = False, template_vars: Optional[Dict[str, Any]] = None
    ) -> defer.Deferred:
        ...

    def get_configuration_history(self, service: str) -> defer.Deferred:
        ...


class ConfigService(IConfigService):
    def __init__(self, db: IDatabaseManager = db_manager):
        self.db = db

    @defer.inlineCallbacks
    def create_configuration(self, service: str, yaml_content: str) -> Generator[int, Any, Any]:
        try:
            cfg = yaml.safe_load(yaml_content)
        except Exception as e:
            raise ValueError(f"Invalid YAML: {e}")
        version = yield self.db.save_configuration(service, cfg)
        defer.returnValue({"service": service, "version": version, "status": "saved"})

    @defer.inlineCallbacks
    def get_configuration(
        self, service: str, version: Optional[int] = None, template: bool = False, template_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        cfg = yield self.db.get_configuration(service, version)
        if cfg is None:
            raise ServiceNotFoundError(service)
        payload = cfg.payload
        if template and template_vars:
            payload = self._apply_template(payload, template_vars)
        defer.returnValue(payload)

    @defer.inlineCallbacks
    def get_configuration(
            self, service: str, version: Optional[int] = None, template: bool = False,
            template_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        cfg = yield self.db.get_configuration(service, version)
        payload = cfg.payload
        if template:
            if template_vars is None:
                template_vars = {}
            payload = self._apply_template(payload, template_vars)

        defer.returnValue(payload)

    def _apply_template(self, payload: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:

        def _render(val):
            if isinstance(val, str):
                try:
                    template = Template(val)
                    return template.render(template_vars)
                except TemplateError as e:
                    return val
            elif isinstance(val, dict):
                return {k: _render(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [_render(v) for v in val]
            else:
                return val

        return _render(payload)

    def _apply_template(self, payload: Dict[str, Any], template_vars: Dict[str, Any]) -> Dict[str, Any]:
        def _render(val):
            if isinstance(val, str):
                try:
                    return Template(val).render(template_vars)
                except TemplateError:
                    return val
            elif isinstance(val, dict):
                return {k: _render(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [_render(v) for v in val]
            else:
                return val
        return _render(payload)

    @defer.inlineCallbacks
    def get_configuration_history(self, service: str) -> Generator[Deferred, Any, Any]:
        history = yield self.db.get_configuration_history(service)
        defer.returnValue([{"version": h.version, "created_at": h.created_at.isoformat()} for h in history])
