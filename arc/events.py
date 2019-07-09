import boto3
import json
from . import reflect

def publish(name, payload):
    arc = reflect()
    arn = arc['events'][name]
    sns = boto3.client('sns')
    return sns.publish(TopicArn=arn, Message=json.dumps(payload))
