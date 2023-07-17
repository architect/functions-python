import json
import urllib.request
import boto3

from . import services
from .lib.utils import use_aws, get_ports

port = None
cache = {}


def parse(event):
    messages = list(map((lambda record: json.loads(record["body"])), event["Records"]))
    if len(messages) == 1:
        return messages[0]
    return messages


def publish(name, payload):
    global port
    local = not use_aws()

    def publish_sandbox(name, payload):
        try:
            dump = json.dumps({"name": name, "payload": payload})
            data = bytes(dump.encode())
            handler = urllib.request.urlopen(f"http://localhost:{port}/queues", data)
            return handler.read().decode("utf-8")
        except Exception as error:
            print("arc.queues.publish to Sandbox failed: " + str(error))
            return data

    def publish_aws(name, payload):
        global cache

        def pub(arn):
            sqs = boto3.client("sqs")
            return sqs.send_message(
                QueueUrl=arn, MessageBody=json.dumps(payload), DelaySeconds=0
            )

        if cache.get(name):
            return pub(cache[name])
        service_map = services()
        cache = service_map["queues"]
        arn = cache[name]
        if not arn:
            raise TypeError(f"{name} event not found")
        return pub(arn)

    if local and port:
        return publish_sandbox(name, payload)
    if local:
        ports = get_ports()
        if not ports.get("events"):
            raise TypeError("Sandbox queues port not found")
        port = ports["events"]
        return publish_sandbox(name, payload)
    return publish_aws(name, payload)
