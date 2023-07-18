# -*- coding: utf-8 -*-
import base64
import json
import pytest

from arc.http import parse_body


def b64encode(string):
    return base64.b64encode(bytes(string, "utf-8")).decode("ascii")


# --------------------------------------------------
#
# Tests ported from @architect/functions project
# Please port back if adding/changing functionality!
#
# --------------------------------------------------

# Bodies
hi = {"hi": "there"}
hi_base64_file = b64encode("hi there\n")  # text file style
hi_form_url = b64encode("hi=there")
hi_text = "hi there"
hi_xml = '<?xml version="1.0"?><hi>there</hi>'

# Content types
json_encoded = {"content-type": "application/json"}
form_url_encoded = {"content-type": "application/x-www-form-urlencoded"}
multi_part_form_data = {"content-type": "multipart/form-data"}
octet_stream = {"content-type": "application/octet-stream"}
text = {"content-type": "text/plain"}
xml_text = {"content-type": "text/xml"}
xml_app = {"content-type": "application/xml"}


# Architect v10+ requests
def test_plain_text():
    mock = {"body": hi_text, "headers": text, "isBase64Encoded": False}
    body = parse_body(mock)
    assert body == hi_text


def test_plain_text_b64():
    mock = {
        "body": b64encode(hi_text),
        "headers": text,
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == hi_text


def test_xml():
    mock = {
        "body": hi_xml,
        "headers": xml_text,
        "isBase64Encoded": False,
    }
    body = parse_body(mock)
    assert body == hi_xml


def test_xml_app():
    mock = {
        "body": hi_xml,
        "headers": xml_app,
        "isBase64Encoded": False,
    }
    body = parse_body(mock)
    assert body == hi_xml


def test_xml_b64():
    mock = {
        "body": b64encode(hi_xml),
        "headers": xml_text,
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == hi_xml


def test_xml_app_b64():
    mock = {
        "body": b64encode(hi_xml),
        "headers": xml_app,
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == hi_xml


# Architect v6+ requests


# HTTP + Lambda v2.0 payloads pass in raw JSON
def test_raw_json():
    mock = {
        "body": json.dumps(hi),
        "headers": json_encoded,
        "isBase64Encoded": False,
    }
    body = parse_body(mock)
    assert body == hi


# Pass through empty body (although in practice we'll never see this, as we transform to empty object)
def test_empty_body():
    mock = {
        "body": None,
        "headers": json_encoded,
    }
    body = parse_body(mock)
    assert body is None


def test_json_b64():
    mock = {
        "body": b64encode(json.dumps(hi)),
        "headers": json_encoded,
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == hi


def test_json_api_b64():
    mock = {
        "body": b64encode(json.dumps(hi)),
        "headers": {"content-type": "application/vnd.api+json"},
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == hi


# Test faulty encoding on JSON posts
def test_raw_json_fails():
    mock = {
        "body": json.dumps(hi),
        "headers": json_encoded,
        "isBase64Encoded": True,
    }
    with pytest.raises(
        ValueError,
        match=r"Invalid request body encoding or invalid JSON",
    ):
        parse_body(mock)


def test_invalid_json_fails():
    mock = {
        "body": b64encode("hello there"),
        "headers": json_encoded,
        "isBase64Encoded": True,
    }
    with pytest.raises(
        ValueError,
        match=r"Invalid request body encoding or invalid JSON",
    ):
        parse_body(mock)


def test_form_url_b64():
    mock = {
        "body": hi_form_url,
        "headers": form_url_encoded,
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == hi


def test_multipart_b64():
    mock = {
        "body": hi_base64_file,
        "headers": multi_part_form_data,
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == {"base64": hi_base64_file}


def test_octet_b64():
    mock = {
        "body": hi_base64_file,
        "headers": octet_stream,
        "isBase64Encoded": True,
    }
    body = parse_body(mock)
    assert body == {"base64": hi_base64_file}


# Architect v5 requests
def test_empty_body_v5():
    mock = {
        "body": {},
        "headers": json_encoded,
    }
    body = parse_body(mock)
    assert body == {}


def test_parsed_json_body():
    mock = {
        "body": hi,
        "headers": json_encoded,
    }
    body = parse_body(mock)
    assert body == hi


def test_parsed_form_url_encoded_body():
    mock = {
        "body": hi,
        "headers": form_url_encoded,
    }
    body = parse_body(mock)
    assert body == hi


def test_parsed_octet_stream_body():
    mock = {
        "body": hi,
        "headers": octet_stream,
    }
    body = parse_body(mock)
    assert body == hi
