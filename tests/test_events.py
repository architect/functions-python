# # -*- coding: utf-8 -*-
import json
from uuid import UUID
import arc


def test_parse():
    data = {"ok": True}
    message = {"Records": [{"Sns": {"Message": json.dumps(data)}}]}
    parsed = arc.events.parse(message)
    assert parsed["ok"] == True
    assert len(parsed) == 1

    message = {
        "Records": [
            {"Sns": {"Message": json.dumps(data)}},
            {"Sns": {"Message": json.dumps(data)}},
        ]
    }
    parsed = arc.events.parse(message)
    assert parsed[0]["ok"] == True
    assert parsed[1]["ok"] == True
    assert len(parsed) == 2


def test_publish(arc_services, sns_client):
    topic_name = "ping"
    sns_client.create_topic(Name=topic_name)
    topics = sns_client.list_topics()

    arc_services(params={f"events/{topic_name}": topics["Topics"][0]["TopicArn"]})
    val = arc.events.publish(name=topic_name, payload={"python": True})
    assert isinstance(val, dict)
    assert "MessageId" in val

    parsed = UUID(val["MessageId"], version=4)
    assert isinstance(parsed, UUID)
