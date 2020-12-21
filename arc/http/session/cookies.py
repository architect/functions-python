import os
import time
from http import cookies
from typing import Optional


def _read_cookie(req, cookie_name: str) -> Optional[str]:
    # Lambda payload version 2 puts the cookies in an array on the request
    if "cookies" in req:
        raw_cookie = ";".join(req.get("cookies"))
    else:
        headers = req.get("headers", {})
        # TODO: uppercase 'Cookie' is not the header name on AWS Lambda; it's
        # lowercase 'cookie' on lambda...
        raw_cookie = headers.get("Cookie", headers.get("cookie", ""))

    jar = cookies.SimpleCookie(raw_cookie)
    cookie = jar.get(cookie_name)
    return None if cookie is None else cookie.value


def _write_cookie(payload: str, cookie_name: str) -> str:
    max_age = int(os.environ.get("SESSION_TTL", 7.884e8))

    jar = cookies.SimpleCookie()
    jar[cookie_name] = payload
    jar[cookie_name]["max-age"] = max_age
    jar[cookie_name]["expires"] = time.time() + max_age * 1000
    jar[cookie_name]["httponly"] = True
    jar[cookie_name]["path"] = "/"

    if "SESSION_DOMAIN" in os.environ:
        jar[cookie_name]["domain"] = os.environ.get("SESSION_DOMAIN")

    if os.environ.get("NODE_ENV") != "testing":
        jar[cookie_name]["secure"] = True

    return jar.output(header="")
