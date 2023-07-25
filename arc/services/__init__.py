import os
import json
import boto3
from arc._lib import use_aws, to_logical_id

_service_map_cache = {}
_ssm_client_cache = None


def _services():
    global _service_map_cache
    global _ssm_client_cache

    testing = os.environ.get("_TESTING")
    if _service_map_cache and not testing:
        return _service_map_cache

    app = os.environ.get("ARC_APP_NAME")
    env = os.environ.get("ARC_ENV")
    sandbox = os.environ.get("ARC_SANDBOX")
    stack = os.environ.get("ARC_STACK_NAME")
    region_name = os.environ.get("AWS_REGION", "us-west-2")

    local = not use_aws()

    if not local and not app and not stack:
        raise TypeError("ARC_APP_NAME and ARC_STACK_NAME env vars not found")

    if local and not app:
        app = "arc-app"

    app_name = stack or to_logical_id(f"{app}-{env}")
    path = f"/{app_name}"

    if local:
        port = 2222
        if sandbox:
            sandbox_config = json.loads(sandbox)
            if not sandbox_config["ports"].get("_arc"):
                raise TypeError("Sandbox internal port not found")
            port = sandbox_config["ports"]["_arc"]

        if not _ssm_client_cache:
            session = boto3.session.Session()
            _ssm_client_cache = session.client(
                service_name="ssm",
                endpoint_url=f"http://localhost:{port}/_arc/ssm",
                region_name=region_name,
            )
    else:
        if not _ssm_client_cache:
            _ssm_client_cache = boto3.client("ssm")

    paginator = _ssm_client_cache.get_paginator("get_parameters_by_path")
    response_iterator = paginator.paginate(Path=path, Recursive=True)
    parameters = []
    for page in response_iterator:
        for entry in page["Parameters"]:
            parameters.append(entry)

    params = dict((x["Name"], x["Value"]) for x in parameters)
    result = {}
    for key in params:
        bits = key.split("/")
        t = bits[2]
        k = bits[3]
        val = params[key]
        if t not in result:
            result[t] = {}
        result[t][k] = val
    _service_map_cache = result
    return _service_map_cache
