# -*- coding: utf-8 -*-
import copy
import json
import arc

# TODO: implement tests when Arc's req/res fixtures can be ported to py; see: https://github.com/architect/req-res-fixtures
simple_req_mock = {
    "version": "2.0",
    "headers": {},
}
session_mock = {"foo": {"bar": 123}, "yak": None}


def make_req(res):
    new = copy.deepcopy(simple_req_mock)
    res_cookie = res["headers"]["set-cookie"]
    new["headers"]["cookie"] = res_cookie.split(";")[0]
    return new


def test_method_exists():
    mock = {"version": "2.0", "headers": {}}
    ok = {"ok": True}
    res = arc.http.res(mock, ok)
    assert res.get("headers")
    assert res.get("statusCode") == 200
    assert res.get("body") == json.dumps(ok)


def test_jwe_session(monkeypatch):
    monkeypatch.setenv("ARC_SESSION_TABLE_NAME", "jwe")

    # Create + write a session
    payload = {"session": copy.deepcopy(session_mock)}
    response = arc.http.res(simple_req_mock, payload)
    req = make_req(response)
    session = arc.http.session_read(req)
    del session["iat"]  # delete issued at timestamp
    assert session == session_mock

    # Mutate / destroy a session
    payload = {"session": {}}
    response = arc.http.res(simple_req_mock, payload)
    req = make_req(response)
    session = arc.http.session_read(req)
    del session["iat"]  # delete issued at timestamp
    assert session == {}


def test_ddb_session(monkeypatch, arc_services, ddb_client):
    tablename = "sessions"
    monkeypatch.setenv("ARC_SESSION_TABLE_NAME", tablename)
    ddb_client.create_table(
        TableName=tablename,
        KeySchema=[{"AttributeName": "_idx", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "_idx", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    tables = ddb_client.list_tables()
    arc_services(params={f"tables/{tablename}": tables["TableNames"][0]})

    # Create + write a session
    payload = {"session": copy.deepcopy(session_mock)}
    response = arc.http.res(simple_req_mock, payload)
    # In the case of DynamoDB sessions, we can keep reusing the same request
    req = make_req(response)
    session = arc.http.session_read(req)
    assert bool(session["_idx"])
    assert bool(session["_secret"])
    assert bool(session["_ttl"])
    session_match = copy.deepcopy(session)
    del session_match["_idx"]
    del session_match["_secret"]
    del session_match["_ttl"]
    assert session_match == session_mock

    # Mutate a session
    payload = {"session": copy.deepcopy(session)}
    payload["session"]["count"] = 0
    arc.http.res(req, payload)
    mutated_session = arc.http.session_read(req)
    # Ensure a new session wasn't created
    assert mutated_session["_idx"] == session["_idx"]
    assert mutated_session["_secret"] == session["_secret"]
    assert bool(mutated_session["_ttl"])
    assert "count" in mutated_session
    assert mutated_session["count"] == 0

    # Destroy session contents
    payload = {"session": {}}
    arc.http.res(req, payload)
    destroyed_session = arc.http.session_read(req)
    assert destroyed_session["_idx"] == session["_idx"]
    assert destroyed_session["_secret"] == session["_secret"]
    assert bool(destroyed_session["_ttl"])
    assert "count" not in destroyed_session
