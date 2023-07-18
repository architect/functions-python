# -*- coding: utf-8 -*-
import jwcrypto
import pytest

from arc.http import session_read, session_write
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
    cookie = session_write({"count": 0})
    mock = {
        "headers": {
            "cookie": cookie,
        },
    }
    session = session_read(mock)
    assert "count" in session
    assert session["count"] == 0


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
        jwcrypto.common.InvalidCEKeyLength,
        match=r"Expected key of length 256 bits, got 48",
    ):
        test_jwe_session(monkeypatch)
    with pytest.raises(
        jwcrypto.common.InvalidCEKeyLength,
        match=r"Expected key of length 256 bits, got 48",
    ):
        test_jwe_read_write()


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
