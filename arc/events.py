import json
import urllib.request
import boto3

from arc import services
from arc.lib import use_aws, get_ports

port = None
cache = {}


def parse(event):
    messages = list(
        map((lambda record: json.loads(record["Sns"]["Message"])), event["Records"])
    )
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
            handler = urllib.request.urlopen(f"http://localhost:{port}/events", data)
            return handler.read().decode("utf-8")
        except Exception as error:
            print("arc.events.publish to Sandbox failed: " + str(error))
            return data

    def publish_aws(name, payload):
        global cache

        def pub(arn):
            sns = boto3.client("sns")
            return sns.publish(TopicArn=arn, Message=json.dumps(payload))

        if cache.get(name):
            return pub(cache[name])
        service_map = services()
        cache = service_map["events"]
        arn = cache[name]
        if not arn:
            raise TypeError(f"{name} event not found")
        return pub(arn)

    if local and port:
        return publish_sandbox(name, payload)
    if local:
        ports = get_ports()
        if not ports.get("events"):
            raise TypeError("Sandbox events port not found")
        port = ports["events"]
        return publish_sandbox(name, payload)
    return publish_aws(name, payload)
