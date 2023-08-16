# # -*- coding: utf-8 -*-
import json
from uuid import UUID
import arc


def test_parse():
    data = {"ok": True}
    message = {"Records": [{"body": json.dumps(data)}]}
    parsed = arc.queues.parse(message)
    assert parsed["ok"] == True
    assert len(parsed) == 1

    message = {
        "Records": [
            {"body": json.dumps(data)},
            {"body": json.dumps(data)},
        ]
    }
    parsed = arc.queues.parse(message)
    assert parsed[0]["ok"] == True
    assert parsed[1]["ok"] == True
    assert len(parsed) == 2


def test_queue_publish(arc_services, sqs_client):
    queue_name = "continuum"
    sqs_client.create_queue(
        QueueName=queue_name + ".fifo", Attributes={"FifoQueue": "true"}
    )
    queues = sqs_client.list_queues()

    arc_services(params={f"queues/{queue_name}": queues["QueueUrls"][0]})
    val = arc.queues.publish(name=queue_name, payload={"python": True})
    assert isinstance(val, dict)
    assert "MessageId" in val

    parsed = UUID(val["MessageId"], version=4)
    assert isinstance(parsed, UUID)
