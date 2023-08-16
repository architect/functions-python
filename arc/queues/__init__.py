import json
import os
import urllib.request
import uuid
import boto3
from arc.services import _services
from arc._lib import use_aws, get_ports

_port = None
_queues_cache = {}
_sqs_client_cache = None


def parse(event):
    messages = list(map((lambda record: json.loads(record["body"])), event["Records"]))
    if len(messages) == 1:
        return messages[0]
    return messages


def publish(name, payload):
    local = not use_aws()

    def publish_sandbox(name, payload):
        try:
            dump = json.dumps({"name": name, "payload": payload})
            data = bytes(dump.encode())
            handler = urllib.request.urlopen(f"http://localhost:{_port}/queues", data)
            return handler.read().decode("utf-8")
        except Exception as error:
            print("arc.queues.publish to Sandbox failed: " + str(error))
            return data

    def publish_aws(name, payload):
        global _queues_cache
        global _sqs_client_cache

        if not _sqs_client_cache:
            _sqs_client_cache = boto3.client("sqs")

        def pub(arn):
            stack = os.environ.get("ARC_STACK_NAME")
            return _sqs_client_cache.send_message(
                QueueUrl=arn,
                MessageBody=json.dumps(payload),
                DelaySeconds=0,
                MessageGroupId=stack,
                MessageDeduplicationId=str(uuid.uuid4()),
            )

        if _queues_cache.get(name):
            return pub(_queues_cache[name])
        service_map = _services()
        _queues_cache = service_map["queues"]
        arn = _queues_cache[name]
        if not arn:
            raise TypeError(f"{name} event not found")
        return pub(arn)

    if local:
        global _port

        if _port:
            return publish_sandbox(name, payload)

        ports = get_ports()
        if not ports.get("events"):
            raise TypeError("Sandbox queues port not found")
        _port = ports["events"]
        return publish_sandbox(name, payload)
    return publish_aws(name, payload)
