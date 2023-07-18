import os
import time
import platform
from http import cookies
from typing import Optional


def _read_cookie(req, cookie_name: str) -> Optional[str]:
    # Lambda payload version 2 puts the cookies in an array on the request
    if "cookies" in req:
        raw_cookie = ";".join(req.get("cookies"))
    else:
        headers = req.get("headers", {})
        raw_cookie = headers.get("cookie", headers.get("Cookie", ""))

    jar = cookies.SimpleCookie(raw_cookie)
    cookie = jar.get(cookie_name)
    if cookie:
        return cookie.value
    return None


def _write_cookie(payload: str, cookie_name: str) -> str:
    ttl = os.environ.get("ARC_SESSION_TTL", os.environ.get("SESSION_TTL", 7.884e8))
    max_age = int(ttl)

    jar = cookies.SimpleCookie()
    jar[cookie_name] = payload
    jar[cookie_name]["max-age"] = max_age
    jar[cookie_name]["expires"] = time.time() + max_age * 1000
    jar[cookie_name]["httponly"] = True
    jar[cookie_name]["path"] = "/"

    # Python 3.7 and below apparently doesn't support samesite
    ver = platform.python_version_tuple()
    if int(ver[1]) > 7:
        jar[cookie_name]["samesite"] = "lax"

    domain = os.environ.get("ARC_SESSION_DOMAIN", os.environ.get("SESSION_DOMAIN"))
    if domain:
        jar[cookie_name]["domain"] = domain

    if os.environ.get("ARC_ENV") != "testing":
        jar[cookie_name]["secure"] = True

    return jar.output(header="")
