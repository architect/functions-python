import math
import os
import time
from typing import Any, Dict

from jwcrypto import jwe, jwk
from jwcrypto.common import base64url_encode, json_decode, json_encode


def _get_key() -> str:
    # 16 bit fallback key size
    fallback = b"1234567890123456"

    # need to STRONGLY encourage setting ARC_APP_SECRET in the docs
    secret = os.environ.get("ARC_APP_SECRET", fallback)

    # truncate key to 16 bits, this matches what node-webtokens does
    # https://github.com/teifip/node-webtokens/blob/master/lib/jwe.js#L299
    secret = secret[16:] if len(secret) > 16 else secret

    return jwk.JWK(k=base64url_encode(secret), kty="oct")


def jwe_read(cookie: str) -> Dict[Any, Any]:
    jwetoken = jwe.JWE()
    jwetoken.deserialize(cookie, key=_get_key())
    return json_decode(jwetoken.payload)


def jwe_write(payload: Dict[Any, Any]) -> str:
    payload = dict(payload)
    payload["iat"] = math.floor(time.time())
    jwetoken = jwe.JWE(
        json_encode(payload),
        json_encode({"alg": "dir", "enc": "A128GCM"}),
        recipient=_get_key(),
    )
    return jwetoken.serialize(compact=True)
