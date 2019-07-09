import boto3
import json
from . import reflect

def publish(name, payload):
    arc = reflect()
    arn = arc['queues'][name]
    sqs = boto3.client('sqs')
    return sqs.send_message(QueueUrl=arn, MessageBody=json.dumps(payload), DelaySeconds=0)
