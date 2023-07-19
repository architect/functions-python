import base64
import copy
import json
from urllib.parse import parse_qsl


def parse_body(req):
    ctype = req["headers"].get("content-type", req["headers"].get("Content-Type"))
    body = req.get("body")
    # We aren't going to support <Arc 6 bodies, which are always empty dicts
    passthru = not body or not req["headers"] or not ctype or not isinstance(body, str)
    if passthru:
        return body
    else:
        # Paranoid deep copy
        request = copy.deepcopy(req)

        def content_type(passed_type):
            return ctype.lower().find(passed_type) != -1

        is_string = isinstance(request.get("body"), str)
        is_base64 = request.get("isBase64Encoded")
        is_parsing = is_string and is_base64
        is_json = (
            content_type("application/json") or content_type("application/vnd.api+json")
        ) and is_string
        is_form_urlencoded = (
            content_type("application/x-www-form-urlencoded") and is_parsing
        )
        is_multi_part_form_data = content_type("multipart/form-data") and is_parsing
        is_octet_stream = content_type("application/octet-stream") and is_parsing
        is_plain_text = content_type("text/plain") and is_parsing
        is_xml = (
            content_type("text/xml") or content_type("application/xml")
        ) and is_parsing

        if is_json:
            try:
                data = (
                    base64.b64decode(request.get("body")).decode("utf-8")
                    if is_base64
                    else request.get("body")
                )
                request["body"] = json.loads(data) or {}
            except:
                raise ValueError("Invalid request body encoding or invalid JSON")

        if is_plain_text or is_xml:
            request["body"] = base64.b64decode(request.get("body")).decode("utf-8")

        if is_form_urlencoded:
            data = base64.b64decode(request.get("body")).decode("utf-8")
            request["body"] = dict(parse_qsl(data))

        if is_multi_part_form_data or is_octet_stream:
            request["body"] = {"base64": request["body"]}

        return request["body"]
