# -*- coding: utf-8 -*-
import urllib.parse
import jose
import pytest
import arc
from arc.http.session.jwe import jwe_write, jwe_read
from arc.http.session.ddb import ddb_write, ddb_read
from arc.http.session.ddb import _sign, _unsign


def test_jwe_read_write():
    payload = {"foo": {"bar": 123}, "yak": None}
    token = jwe_write(payload)
    parsed = jwe_read(token)
    del parsed["iat"]  # delete issued at timestamp
    assert parsed == payload


def test_jwe_session(monkeypatch):
    monkeypatch.setenv("ARC_SESSION_TABLE_NAME", "jwe")
    # Write a session
    cookie = arc.http.session_write({"count": 0})
    mock = {
        "headers": {
            "cookie": cookie,
        },
    }
    session = arc.http.session_read(mock)
    assert "count" in session
    assert session["count"] == 0
    # Destroy a session
    cookie = arc.http.session_write({})
    mock = {
        "headers": {
            "cookie": cookie,
        },
    }
    session = arc.http.session_read(mock)
    assert "count" not in session


def test_custom_key(monkeypatch):
    monkeypatch.setenv("ARC_APP_SECRET", "abcdefghijklmnopqrstuvwxyz012345")
    test_jwe_session(monkeypatch)
    test_jwe_read_write()


def test_long_key(monkeypatch):
    monkeypatch.setenv("ARC_APP_SECRET", "abcdefghijklmnopqrstuvwxyz012345abc")
    test_jwe_session(monkeypatch)
    test_jwe_read_write()


def test_short_key(monkeypatch):
    monkeypatch.setenv("ARC_APP_SECRET", "123456")
    with pytest.raises(
        jose.exceptions.JWKError,
        match=r"Key must be 256 bit for alg A256GCM",
    ):
        test_jwe_session(monkeypatch)
    with pytest.raises(
        jose.exceptions.JWKError,
        match=r"Key must be 256 bit for alg A256GCM",
    ):
        test_jwe_read_write()


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

    # Write a session
    payload = {"_idx": "abc", "count": 0}
    cookie = arc.http.session_write(payload)
    mock = {
        "headers": {
            "cookie": cookie,
        }
    }
    session = arc.http.session_read(mock)
    assert "count" in session
    assert session["count"] == 0

    # Ensure URI encoding (inbound from API Gateway) doesn't break cookie validation
    idx = cookie.split(";")[0][6:]  # Strip `_idx=`
    encoded_cookie = "_idx=" + urllib.parse.quote(idx)
    mock = {
        "headers": {
            "cookie": encoded_cookie,
        },
    }
    session = arc.http.session_read(mock)
    assert "count" in session
    assert session["count"] == 0

    # Destroy a session
    cookie = arc.http.session_write({"_idx": "abc"})
    mock = {
        "headers": {
            "cookie": cookie,
        }
    }
    session = arc.http.session_read(mock)
    assert "count" not in session


def test_ddb_sign_unsign():
    original = "123456"
    secret = "1234567890"
    signed = _sign(original, secret)
    unsigned, valid = _unsign(signed, secret)
    assert valid == True
    assert original == unsigned


def test_ddb_sign_unsign_fail():
    original = "123456"
    secret = "1234567890"
    signed = _sign(original, secret)
    unsigned, valid = _unsign(signed, secret + "1234")
    assert valid == False


def test_ddb_read_write(arc_services, ddb_client):
    tablename = "sessions"
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

    payload = {"_idx": "abc", "foo": {"bar": 123}, "yak": None}
    token = ddb_write(payload, tablename)
    parsed = ddb_read(token, tablename)
    del parsed["_ttl"]  # delete ttl timestamp
    assert parsed == payload
