import os
import time
import platform
from http import cookies
from typing import Optional

COOKIE_NAME: str = "_idx"


def _read_cookie(req) -> Optional[str]:
    # Lambda payload version 2 puts the cookies in an array on the request
    if "cookies" in req:
        raw_cookie = ";".join(req.get("cookies"))
    else:
        headers = req.get("headers", {})
        raw_cookie = headers.get("cookie", headers.get("Cookie", ""))

    jar = cookies.SimpleCookie(raw_cookie)
    cookie = jar.get(COOKIE_NAME)
    if cookie:
        return cookie.value
    return None


def _write_cookie(payload: str) -> str:
    ttl = os.environ.get("ARC_SESSION_TTL", os.environ.get("SESSION_TTL", 7.884e8))
    max_age = int(ttl)

    jar = cookies.SimpleCookie()
    jar[COOKIE_NAME] = payload
    jar[COOKIE_NAME]["max-age"] = max_age
    jar[COOKIE_NAME]["expires"] = time.time() + max_age * 1000
    jar[COOKIE_NAME]["httponly"] = True
    jar[COOKIE_NAME]["path"] = "/"

    # Python 3.7 and below apparently doesn't support samesite
    ver = platform.python_version_tuple()
    if int(ver[1]) > 7:
        jar[COOKIE_NAME]["samesite"] = "lax"

    domain = os.environ.get("ARC_SESSION_DOMAIN", os.environ.get("SESSION_DOMAIN"))
    if domain:
        jar[COOKIE_NAME]["domain"] = domain

    if os.environ.get("ARC_ENV") != "testing":
        jar[COOKIE_NAME]["secure"] = True

    return jar.output(header="")
