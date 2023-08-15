import json
import urllib.request
import boto3
from arc.services import _services
from arc._lib import use_aws, get_ports

_port = None
_events_cache = {}
_sns_client_cache = None


def parse(event):
    messages = list(
        map((lambda record: json.loads(record["Sns"]["Message"])), event["Records"])
    )
    if len(messages) == 1:
        return messages[0]
    return messages


def publish(name, payload):
    local = not use_aws()

    def publish_sandbox(name, payload):
        try:
            dump = json.dumps({"name": name, "payload": payload})
            data = bytes(dump.encode())
            handler = urllib.request.urlopen(f"http://localhost:{_port}/events", data)
            return handler.read().decode("utf-8")
        except Exception as error:
            print("arc.events.publish to Sandbox failed: " + str(error))
            return data

    def publish_aws(name, payload):
        global _events_cache
        global _sns_client_cache

        if not _sns_client_cache:
            _sns_client_cache = boto3.client("sns")

        def pub(arn):
            return _sns_client_cache.publish(TopicArn=arn, Message=json.dumps(payload))

        if _events_cache.get(name):
            return pub(_events_cache[name])
        service_map = _services()
        _events_cache = service_map["events"]
        arn = _events_cache[name]
        if not arn:
            raise TypeError(f"{name} event not found")
        return pub(arn)

    if local:
        global _port

        if _port:
            return publish_sandbox(name, payload)

        ports = get_ports()
        if not ports.get("events"):
            raise TypeError("Sandbox events port not found")
        _port = ports["events"]
        return publish_sandbox(name, payload)
    return publish_aws(name, payload)
