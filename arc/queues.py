import boto3
import json
import urllib.request

from . import reflect

def publish(name, payload):
    if os.environ.get('NODE_ENV') == 'testing':
        try:
            dump = json.dumps({'name':name, 'payload':payload})
            data = bytes(dump.encode())
            handler = urllib.request.urlopen('http://localhost:3334/queues', data)
            return handler.read().decode('utf-8')
        except Exception as e:
            print('arc.queues.publish to sandbox failed: '+ str(e))
            return data
    else:
        arc = reflect()
        arn = arc['queues'][name]
        sqs = boto3.client('sqs')
        return sqs.send_message(QueueUrl=arn, MessageBody=json.dumps(payload), DelaySeconds=0)
