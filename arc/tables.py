import os
import boto3
from arc import services
from arc.lib import use_aws, get_ports

port = None
tablename_cache = {}
db_client_cache = {}


def name(tablename):
    """Get generated DynamoDB table name.

    Keyword arguments:
    tablename -- the name defined in app.arc
    """
    global tablename_cache

    if tablename_cache.get(tablename):
        return tablename_cache[tablename]

    service_map = services()
    if service_map.get("tables"):
        tablename_cache = service_map["tables"]

    if not tablename_cache.get(tablename):
        raise NameError('tablename "' + tablename + '" not found')
    return tablename_cache[tablename]


def table(tablename):
    """Get a DynamoDB.Table client for given table name.

    Keyword arguments:
    tablename -- the name defined in .arc

    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#table
    """

    if db_client_cache.get(tablename):
        return db_client_cache[tablename]

    global port
    local = not use_aws()

    if local:
        if not port:
            ports = get_ports()
            if not ports.get("tables"):
                raise TypeError("Sandbox tables port not found")
            port = ports["tables"]
        region = os.environ.get("AWS_REGION")
        region_name = region or "us-west-2"
        db = boto3.resource(
            "dynamodb", endpoint_url=f"http://localhost:{port}", region_name=region_name
        )
    else:
        db = boto3.resource("dynamodb")
    db_client_cache[tablename] = db.Table(name(tablename))
    return db_client_cache[tablename]
