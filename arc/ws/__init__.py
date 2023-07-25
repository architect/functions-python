import os
import re
import json
import boto3
from arc._lib import use_aws, get_ports

_api = None
_port = None


def instantiate_api():
    global _api
    global _port
    local = not use_aws()

    if not _api:
        if local:
            if not _port:
                ports = get_ports()
                if not ports.get("_arc"):
                    raise TypeError("Sandbox internal port not found")
                _port = ports["_arc"]
            endpoint_url = f"http://localhost:{_port}/_arc/ws"
            region_name = os.environ.get("AWS_REGION", "us-west-2")
            _api = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=endpoint_url,
                region_name=region_name,
            )
        else:
            wss_url = os.environ.get("ARC_WSS_URL")
            endpoint_url = re.sub(r"^ws", "http", wss_url)
            _api = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)


def api():
    instantiate_api()
    return _api


def send(id, payload):
    instantiate_api()
    return _api.post_to_connection(Data=json.dumps(payload), ConnectionId=id)


def close(id):
    instantiate_api()
    return _api.delete_connection(ConnectionId=id)


def info(id):
    instantiate_api()
    return _api.get_connection(ConnectionId=id)
