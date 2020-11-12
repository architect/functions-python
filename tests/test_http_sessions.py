# -*- coding: utf-8 -*-
from arc.http import session_read, session_write
from arc.http.session.jwe import _create_jwe, _parse_jwe


def test_jwe_read_write():
    payload = {"foo": {"bar": 123}, "yak": None}
    token = _create_jwe(payload)
    parsed = _parse_jwe(token)
    del parsed["iat"]  # delete issued at timestamp
    assert parsed == payload


def test_jwe_cookies(monkeypatch):
    monkeypatch.setenv("SESSION_TABLE_NAME", "jwe")
    cookie = session_write({"count": 0})
    mock = {
        "headers": {
            "cookie": cookie,
        },
    }

    session = session_read(mock)
    assert "count" in session
    assert session["count"] == 0
