import os
import boto3
import json
import urllib.request#, urllib.parse

from . import reflect

def publish(name, payload):
    if os.environ.get('NODE_ENV') == 'testing':
        try:
            dump = json.dumps({'name':name, 'payload':payload})
            data = bytes(dump.encode())
            #data = bytes(urllib.parse.urlencode(dump).encode())
            handler = urllib.request.urlopen('http://localhost:3334/events', data)
            return handler.read().decode('utf-8')
        except Exception as e:
            print('arc.events.publish to sandbox failed: '+ str(e))
            return data
    else:
        arc = reflect()
        arn = arc['events'][name]
        sns = boto3.client('sns')
        return sns.publish(TopicArn=arn, Message=json.dumps(payload))
