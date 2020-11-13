import math
import os
import time
from http import cookies
from typing import Any, Dict

from jwcrypto import jwe, jwk
from jwcrypto.common import base64url_encode, json_decode, json_encode

COOKIE_NAME: str = "_idx"


def _get_key() -> str:
    # 16 bit fallback key size
    fallback = b"1234567890123456"

    # need to STRONGLY encourage setting ARC_APP_SECRET in the docs
    secret = os.environ.get("ARC_APP_SECRET", fallback)

    # truncate key to 16 bits, this matches what node-webtokens does
    # https://github.com/teifip/node-webtokens/blob/master/lib/jwe.js#L299
    secret = secret[16:] if len(secret) > 16 else secret

    return jwk.JWK(k=base64url_encode(secret), kty="oct")


def _create_jwe(payload: Dict[Any, Any]) -> str:
    payload = dict(payload)
    payload["iat"] = math.floor(time.time())
    jwetoken = jwe.JWE(
        json_encode(payload),
        json_encode({"alg": "dir", "enc": "A128GCM"}),
        recipient=_get_key(),
    )
    return jwetoken.serialize(compact=True)


def _parse_jwe(token: str) -> Dict[Any, Any]:
    jwetoken = jwe.JWE()
    jwetoken.deserialize(token, key=_get_key())
    return json_decode(jwetoken.payload)


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
