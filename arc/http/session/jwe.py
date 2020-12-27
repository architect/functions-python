import math
import os
import time
import json
from http import cookies
from typing import Any, Dict

from jose import jwe
from jose.utils import base64url_decode

COOKIE_NAME: str = "_idx"


def _get_key() -> str:
    # 32 bit key size
    fallback = b"1234567890123456"

    # need to STRONGLY encourage setting ARC_APP_SECRET in the docs
    return os.environ.get("ARC_APP_SECRET", fallback)


def _create_jwe(payload: Dict[Any, Any]) -> str:
    payload = dict(payload)
    payload["iat"] = math.floor(time.time())
    encrypted = jwe.encrypt(
        json.dumps(payload), _get_key(), algorithm="dir", encryption="A128GCM"
    )
    return encrypted.decode("utf-8")


def _parse_jwe(token: str) -> Dict[Any, Any]:
    payload = jwe.decrypt(token, _get_key())
    return json.loads(payload)


def jwe_read(req) -> Dict[Any, Any]:
    #
    # reads req cookie and returns token payload or an empty object
    #

    # Lambda payload version 2 puts the cookies in an array on the request
    if "cookies" in req:
        raw_cookie = ";".join(req.get("cookies"))
    else:
        headers = req.get("headers", {})
        # TODO: uppercase 'Cookie' is not the header name on AWS Lambda; it's
        # lowercase 'cookie' on lambda...
        raw_cookie = headers.get("Cookie", headers.get("cookie", ""))

    jar = cookies.SimpleCookie(raw_cookie)
    try:
        parsed = _parse_jwe(jar.get(COOKIE_NAME).value)
    except Exception as ex:
        parsed = {}

    return parsed


#
#  creates a Set-Cookie header with token payload encrypted
#
def jwe_write(payload: Dict[Any, Any]) -> str:
    max_age = int(os.environ.get("SESSION_TTL", 7.884e8))

    jar = cookies.SimpleCookie()
    jar[COOKIE_NAME] = _create_jwe(payload)
    jar[COOKIE_NAME]["max-age"] = max_age
    jar[COOKIE_NAME]["expires"] = time.time() + max_age * 1000
    jar[COOKIE_NAME]["httponly"] = True
    jar[COOKIE_NAME]["path"] = "/"

    if "SESSION_DOMAIN" in os.environ:
        jar[COOKIE_NAME]["domain"] = os.environ.get("SESSION_DOMAIN")

    if os.environ.get("NODE_ENV") != "testing":
        jar[COOKIE_NAME]["secure"] = True

    return jar.output(header="")
