import gzip
import os
from base64 import b64encode
import simplejson as _json

from arc.http.session import session_read, session_write
from .binary_types import binary_types
from ..._lib import get_session_table


def res(req, params):
    def res_is(t):
        return isinstance(params, t)

    is_error = res_is(Exception)

    # Handle HTTP API v2.0 payload scenarios, which have some very strange edges
    if req.get("version") == "2.0":
        keys = list(params.keys()) if res_is(dict) else []

        # New school AWS
        known_params = [
            "statusCode",
            "body",
            "headers",
            "isBase64Encoded",
            "cookies",
        ]
        has_known_params = lambda p: p in known_params
        # Old school Arc
        tidy_params = ["code", "cookie", "cors", "location", "session", "status"]
        has_tidy_params = lambda p: p in tidy_params
        # Older school Arc
        statically_bound = ["html", "css", "js", "text", "json", "xml"]
        is_statically_bound = lambda p: p in statically_bound

        # Handle scenarios where we have a known parameter returned
        if (
            res_is(dict)
            and not res_is(list)
            and (
                any(has_known_params(k) for k in keys)
                or any(has_tidy_params(k) for k in keys)
                or any(is_statically_bound(k) for k in keys)
            )
        ):
            pass

        elif is_error:
            pass

        # Handle scenarios where arbitrary stuff is returned to be JSONified
        elif (
            res_is(dict)
            or res_is(list)
            or res_is(bytes)
            or res_is((int, float, complex))
            or (res_is(str) and len(params))
        ):
            params = {"body": _json.dumps(params)}

        # Not returning is actually valid now lolnothingmatters
        elif params is None:
            params = {}

    body_is_buffer = isinstance(params.get("body"), bytes)

    # Response defaults
    #   where possible, normalize headers to pascal-kebab case (lolsigh)
    # Body
    body = params.get("body", "")

    # Headers: cache-control
    cache_control = (
        params.get("cache_control")
        or params.get("cacheControl")
        or params.get("headers", {}).get("cache-control")
        or params.get("headers", {}).get("Cache-Control")
        or ""
    )
    if "Cache-Control" in params.get("headers", {}):
        del params["headers"]["Cache-Control"]  # Clean up improper casing

    # Headers: content-encoding
    content_type = (
        params.get("type")
        or params.get("headers", {}).get("content-type")
        or params.get("headers", {}).get("Content-Type")
        or "application/json; charset=utf8"
    )
    if "Content-Type" in params.get("headers", {}):
        del params["headers"]["Content-Type"]  # Clean up improper casing

    # Headers: content-encoding
    encoding = params.get("headers", {}).get("content-encoding") or params.get(
        "headers", {}
    ).get("Content-Encoding")
    if "Content-Encoding" in params.get("headers", {}):
        del params["headers"]["Content-Encoding"]  # Clean up improper casing
    accept_encoding = req.get("headers", {}).get("accept-encoding") or req.get(
        "headers", {}
    ).get("Accept-Encoding")

    # Cross-origin ritual sacrifice
    cors = params.get("cors")

    # Old school convenience response params
    # As of Node.js Functions v4 we will keep these around for all eternity
    if params.get("html"):
        content_type = "text/html; charset=utf8"
        body = params["html"]
    elif params.get("css"):
        content_type = "text/css; charset=utf8"
        body = params["css"]
    elif params.get("js"):
        content_type = "text/javascript; charset=utf8"
        body = params["js"]
    elif params.get("text"):
        content_type = "text/plain; charset=utf8"
        body = params["text"]
    elif params.get("json"):
        content_type = "application/json; charset=utf8"
        body = _json.dumps(params["json"])
    elif params.get("xml"):
        content_type = "application/xml; charset=utf8"
        body = params["xml"]

    # Status
    provided_status = (
        params.get("status")
        or params.get("code")
        or params.get("statusCode")
        or params.get("status_code")
    )
    status_code = provided_status or 200

    res = {
        "headers": {"content-type": content_type, **params.get("headers", {})},
        "statusCode": status_code,
        "body": body,
    }

    # REST API stuff
    if params.get("multiValueHeaders"):
        res["multiValueHeaders"] = params["multiValueHeaders"]
    # HTTP API stuff
    if params.get("cookies"):
        res["cookies"] = params["cookies"]

    # Error override
    if is_error:
        status_code = provided_status or 500
        title = str(params)
        # TODO improve this output pls!
        res = {"statusCode": status_code, "title": title, "message": title}

    # Set and/or update headers
    headers = res["headers"]
    if cache_control:
        headers["cache-control"] = cache_control
    anti_cache = (
        "text/html" in content_type
        or "application/json" in content_type
        or "application/vnd.api+json" in content_type
        or params.get("location")
    )
    if headers and "cache-control" not in headers and anti_cache:
        headers[
            "cache-control"
        ] = "no-cache, no-store, must-revalidate, max-age=0, s-maxage=0"
    elif headers and "cache-control" not in headers:
        headers[
            "cache-control"
        ] = "max-age=86400"  # Default cache to one day unless otherwise specified
    if cors:
        headers["access-control-allow-origin"] = "*"
    if params.get("isBase64Encoded"):
        res["isBase64Encoded"] = True
    if params.get("location"):
        res["statusCode"] = provided_status or 302
        res["headers"]["location"] = params["location"]
    if params.get("cookie"):
        res["headers"]["set-cookie"] = params["cookie"]

    # Handle body encoding (if necessary)
    content_type = headers.get("content-type", "").split(";")[0]
    is_binary = content_type in binary_types
    body_is_string = isinstance(res["body"], str)

    def b64enc(i):
        return b64encode(i).decode("ascii")

    # TODO add support for brotli
    def compress(body):
        res["headers"]["content-encoding"] = "gzip"
        return gzip.compress(body)

    # Compress, encode, and flag buffer responses

    should_compress = (
        req.get("version")
        and not params.get("isBase64Encoded")
        and not encoding
        and accept_encoding
        and params.get("compression") != False
    )
    accepts_gzip = False
    if accept_encoding:
        if "gzip" in accept_encoding.split(", "):
            accepts_gzip = True
    # Legacy API Gateway (REST, i.e. !req.version) handles its own compression, so don't double-compress / encode
    if body_is_buffer:
        if should_compress and accepts_gzip:
            body = compress(res["body"])
        else:
            body = res["body"]
        res["body"] = b64enc(body)
        res["isBase64Encoded"] = True
    # Body is likely already base64 encoded & has binary MIME type, so just flag it
    elif body_is_string and is_binary:
        res["isBase64Encoded"] = True
    # Compress, encode, and flag string responses
    elif body_is_string and should_compress and accepts_gzip:
        body = compress(bytes(res["body"], "utf-8"))
        res["body"] = b64enc(body)
        res["isBase64Encoded"] = True

    # Save the passed session
    if params.get("session") is not None:
        # In JWE any passed session payload is the new session
        session = params["session"]
        if get_session_table() != "jwe":
            # In Dynamo, we have to figure out which session we're using
            read = session_read(req)
            # Set up session object prioritizing passed session payload over db
            meta = {
                "_idx": session.get("_idx", read.get("_idx")),
                "_secret": session.get("_secret", read.get("_secret")),
                "_ttl": session.get("_ttl", read.get("_ttl")),
            }
            # Then merge passed session payload data
            session.update(meta)

        res["headers"]["set-cookie"] = session_write(session)

    return res
