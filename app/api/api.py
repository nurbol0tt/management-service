import json
from typing import Dict, Any, Optional
from klein import Klein
from twisted.internet.defer import inlineCallbacks
from twisted.web.http import BAD_REQUEST, NOT_FOUND, INTERNAL_SERVER_ERROR, CONFLICT

from app.services.exceptions import VersionNotFoundError, ServiceNotFoundError
from app.services.service import ConfigService, IConfigService

app = Klein()
config_service: IConfigService = ConfigService()


def _json_response(data: dict, status: int = 200) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def _get_query_params(request) -> Dict[str, Any]:
    params = {}
    for key, values in request.args.items():
        k = key.decode("utf-8")
        if len(values) == 1:
            v = values[0].decode("utf-8")
            if v.isdigit():
                params[k] = int(v)
            elif v.lower() in ("true", "1"):
                params[k] = True
            elif v.lower() in ("false", "0"):
                params[k] = False
            else:
                params[k] = v
        else:
            params[k] = [v.decode("utf-8") for v in values]
    return params


@app.route("/", methods=["GET"])
def root(request):
    request.setHeader(b"Content-Type", b"application/json")
    info = {
        "service": "Configuration Management Service",
        "version": "1.0.0",
        "endpoints": {
            "POST /config/{service}": "Upload new configuration",
            "GET /config/{service}": "Get configuration (supports ?version=N and ?template=1)",
            "GET /config/{service}/history": "Get configuration history",
        },
    }
    return _json_response(info)


@app.route("/config/<string:service>", methods=["POST"])
@inlineCallbacks
def upload_config(request, service: str):
    request.setHeader(b"Content-Type", b"application/json")
    content = request.content.read().decode("utf-8")
    if not content.strip():
        request.setResponseCode(BAD_REQUEST)
        return _json_response({"error": "Empty body"}, BAD_REQUEST)
    try:
        result = yield config_service.create_configuration(service, content)
        request.setResponseCode(201)
        return _json_response(result, 201)
    except Exception as e:
        status = CONFLICT if "already exists" in str(e) else INTERNAL_SERVER_ERROR
        request.setResponseCode(status)
        return _json_response({"error": str(e)}, status)


@app.route("/config/<string:service>", methods=["GET"])
@inlineCallbacks
def get_config(request, service: str):
    request.setHeader(b"Content-Type", b"application/json")
    params = _get_query_params(request)
    version = params.get("version")
    template = params.get("template", False)
    template_vars: Optional[dict] = None
    if template:
        try:
            body = request.content.read().decode("utf-8")
            if body.strip():
                template_vars = json.loads(body)
        except Exception:
            template_vars = {}

    try:
        result = yield config_service.get_configuration(
            service, version, template, template_vars
        )
        return _json_response(result)
    except ServiceNotFoundError:
        request.setResponseCode(NOT_FOUND)
        return _json_response({"error": f"Service '{service}' not found"}, NOT_FOUND)
    except VersionNotFoundError as e:
        request.setResponseCode(NOT_FOUND)
        return _json_response(
            {"error": f"Version {e.version} not found for service '{e.service}'"}, NOT_FOUND
        )
    except Exception:
        request.setResponseCode(INTERNAL_SERVER_ERROR)
        return _json_response({"error": "Internal server error"}, INTERNAL_SERVER_ERROR)

@app.route("/config/<string:service>/history", methods=["GET"])
@inlineCallbacks
def get_config_history(request, service: str):
    request.setHeader(b"Content-Type", b"application/json")
    try:
        result = yield config_service.get_configuration_history(service)
        return _json_response(result)
    except Exception as e:
        request.setResponseCode(INTERNAL_SERVER_ERROR)
        return _json_response({"error": str(e)}, INTERNAL_SERVER_ERROR)
