import os
import re
import json
import boto3

from .lib.utils import use_aws, get_ports

port = None
_api = None


def instantiate_api():
    global port
    global _api
    local = not use_aws()

    if not _api:
        if local:
            if not port:
                ports = get_ports()
                if not ports.get("_arc"):
                    raise TypeError("Sandbox internal port not found")
                port = ports["_arc"]
            endpoint_url = f"http://localhost:{port}/_arc/ws"
            print("endpoint_url", endpoint_url)
            region = os.environ.get("AWS_REGION")
            region_name = region or "us-west-2"
            _api = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=endpoint_url,
                region_name=region_name,
            )
        else:
            wss_url = os.environ.get("ARC_WSS_URL")
            endpoint_url = re.sub(r"^ws", "http", wss_url)
            _api = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)


def send(id, payload):
    instantiate_api()
    return _api.post_to_connection(Data=json.dumps(payload), ConnectionId=id)


def close(id):
    instantiate_api()
    return _api.delete_connection(ConnectionId=id)


def info(id):
    instantiate_api()
    return _api.get_connection(ConnectionId=id)
