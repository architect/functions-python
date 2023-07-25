import math
import os
import time
from typing import Any, Dict

from jwcrypto import jwe, jwk
from jwcrypto.common import base64url_encode, json_decode, json_encode

_algos = {
    # 256 bit (32 octet) key size
    "A256GCM": "12345678901234567890123456789012",
    # 192 bit (24 octet) key size
    "A192GCM": "123456789012345678901234",
    # 128 bit (16 octet) key size
    "A128GCM": "1234567890123456",
}
_enc = None
_key = None


def _setup_crypto():
    global _enc
    global _key
    _enc = os.environ.get("ARC_APP_SECRET_ALGO", "A256GCM")
    if not _algos.get(_enc):
        err = f"Invalid token algorithm, must be one of: {', '.join(_algos.keys())}"
        raise NameError(err)

    # Strongly encourage setting ARC_APP_SECRET, fall back to something dumb and compatible
    secret = os.environ.get("ARC_APP_SECRET", _algos[_enc])

    # Truncate key if necessary, this matches what node-webtokens does
    # https://github.com/teifip/node-webtokens/blob/master/lib/jwe.js#L299
    if len(secret) > len(_algos[_enc]):
        secret = secret[0 : len(_algos[_enc])]

    _key = jwk.JWK(k=base64url_encode(secret), kty="oct")


def jwe_read(cookie: str) -> Dict[Any, Any]:
    _setup_crypto()
    jwetoken = jwe.JWE()
    jwetoken.deserialize(cookie, key=_key)
    return json_decode(jwetoken.payload)


def jwe_write(payload: Dict[Any, Any]) -> str:
    _setup_crypto()
    payload = dict(payload)
    payload["iat"] = math.floor(time.time())
    jwetoken = jwe.JWE(
        json_encode(payload),
        json_encode({"alg": "dir", "enc": _enc}),
        recipient=_key,
    )
    return jwetoken.serialize(compact=True)
