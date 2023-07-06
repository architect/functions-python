# # -*- coding: utf-8 -*-
from uuid import UUID

import pytest

import arc.queues


@pytest.mark.filterwarnings("ignore:the imp module is deprecated")
def test_queue_publish(arc_services, sqs_client):
    queue_name = "continuum"
    sqs_client.create_queue(QueueName=queue_name)
    queues = sqs_client.list_queues()

    arc_services(params={f"queues/{queue_name}": queues["QueueUrls"][0]})
    val = arc.queues.publish(name=queue_name, payload={"python": True})
    assert isinstance(val, dict)
    assert "MessageId" in val

    parsed = UUID(val["MessageId"], version=4)
    assert isinstance(parsed, UUID)
