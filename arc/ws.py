import boto3
import json
from . import reflect

def send(id, payload):
    arc = reflect()
    https = arc['ws']['https']
    api = boto3.client('apigatewaymanagementapi', endpoint_url=https)
    return api.post_to_connection(Data=json.dumps(payload), ConnectionId=id)
