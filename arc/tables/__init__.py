import os
import boto3
from arc.services import _services
from arc._lib import use_aws, get_ports

_port = None
_tables_cache = {}
_dynamo_client_cache = None  # The boto3 DynamoDB client
_dynamo_clients_cache = {}  # Instantiated Dynamo table resources


def name(tablename):
    """Get generated DynamoDB table name.

    Keyword arguments:
    tablename -- the name defined in app.arc
    """
    global _tables_cache

    if _tables_cache.get(tablename):
        return _tables_cache[tablename]

    service_map = _services()
    if service_map.get("tables"):
        _tables_cache = service_map["tables"]

    if not _tables_cache.get(tablename):
        raise NameError('tablename "' + tablename + '" not found')
    return _tables_cache[tablename]


def table(tablename):
    """Get a DynamoDB.Table client for given table name.

    Keyword arguments:
    tablename -- the name defined in .arc

    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#table
    """

    global _dynamo_client_cache
    global _dynamo_clients_cache

    if _dynamo_clients_cache.get(tablename):
        return _dynamo_clients_cache[tablename]

    local = not use_aws()

    if local:
        global _port

        if not _port:
            ports = get_ports()
            if not ports.get("tables"):
                raise TypeError("Sandbox tables port not found")
            _port = ports["tables"]
        region_name = os.environ.get("AWS_REGION", "us-west-2")
        if not _dynamo_client_cache:
            _dynamo_client_cache = boto3.resource(
                "dynamodb",
                endpoint_url=f"http://localhost:{_port}",
                region_name=region_name,
            )
    else:
        if not _dynamo_client_cache:
            _dynamo_client_cache = boto3.resource("dynamodb")

    _dynamo_clients_cache[tablename] = _dynamo_client_cache.Table(name(tablename))
    return _dynamo_clients_cache[tablename]
