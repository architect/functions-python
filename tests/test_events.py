# # -*- coding: utf-8 -*-
from uuid import UUID

import pytest

import arc.events


@pytest.mark.filterwarnings("ignore:the imp module is deprecated")
def test_publish(arc_reflection, sns_client):
    topic_name = "ping"
    sns_client.create_topic(Name=topic_name)
    topics = sns_client.list_topics()

    arc_reflection(params={f"events/{topic_name}": topics["Topics"][0]["TopicArn"]})
    val = arc.events.publish(name=topic_name, payload={"python": True})
    assert isinstance(val, dict)
    assert "MessageId" in val

    parsed = UUID(val["MessageId"], version=4)
    assert isinstance(parsed, UUID)
