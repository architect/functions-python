import boto3
import json

from . import reflect

def send(id, payload):
    if os.environ.get('NODE_ENV') == 'testing':
        try:
            dump = json.dumps({'id':id, 'payload':payload})
            data = bytes(dump.encode())
            handler = urllib.request.urlopen('http://localhost:3333/__arc', data)
            return handler.read().decode('utf-8')
        except Exception as e:
            print('arc.ws.send to sandbox failed: '+ str(e))
            return data
    else:
        arc = reflect()
        https = arc['ws']['https']
        api = boto3.client('apigatewaymanagementapi', endpoint_url=https)
        return api.post_to_connection(Data=json.dumps(payload), ConnectionId=id)
