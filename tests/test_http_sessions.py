# -*- coding: utf-8 -*-
import jwcrypto
import pytest

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


def test_custom_key(monkeypatch):
    monkeypatch.setenv("ARC_APP_SECRET", "abcdefghijklmnop")
    test_jwe_cookies(monkeypatch)
    test_jwe_read_write()


def test_long_key(monkeypatch):
    monkeypatch.setenv("ARC_APP_SECRET", "12345678901234567890123456789012")
    test_jwe_cookies(monkeypatch)
    test_jwe_read_write()


def test_short_key(monkeypatch):
    monkeypatch.setenv("ARC_APP_SECRET", "123456")
    with pytest.raises(
        jwcrypto.common.InvalidCEKeyLength,
        match=r"Expected key of length 128 bits, got 48",
    ):
        test_jwe_cookies(monkeypatch)

    with pytest.raises(
        jwcrypto.common.InvalidCEKeyLength,
        match=r"Expected key of length 128 bits, got 48",
    ):
        test_jwe_read_write()
