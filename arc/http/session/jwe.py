import math
import os
import time
from typing import Any, Dict

from jwcrypto import jwe, jwk
from jwcrypto.common import base64url_encode, json_decode, json_encode

algos = {
    # 256 bit (32 octet) key size
    "A256GCM": "12345678901234567890123456789012",
    # 192 bit (24 octet) key size
    "A192GCM": "123456789012345678901234",
    # 128 bit (16 octet) key size
    "A128GCM": "1234567890123456",
}
enc = None
key = None


def _setup_crypto():
    global enc
    global key
    enc = os.environ.get("ARC_APP_SECRET_ALGO", "A256GCM")
    if not algos.get(enc):
        err = f"Invalid token algorithm, must be one of: {', '.join(algos.keys())}"
        raise NameError(err)

    # Strongly encourage setting ARC_APP_SECRET, fall back to something dumb and compatible
    secret = os.environ.get("ARC_APP_SECRET", algos[enc])

    # Truncate key if necessary, this matches what node-webtokens does
    # https://github.com/teifip/node-webtokens/blob/master/lib/jwe.js#L299
    if len(secret) > len(algos[enc]):
        secret = secret[0 : len(algos[enc])]

    key = jwk.JWK(k=base64url_encode(secret), kty="oct")


def jwe_read(cookie: str) -> Dict[Any, Any]:
    _setup_crypto()
    jwetoken = jwe.JWE()
    jwetoken.deserialize(cookie, key=key)
    return json_decode(jwetoken.payload)


def jwe_write(payload: Dict[Any, Any]) -> str:
    _setup_crypto()
    payload = dict(payload)
    payload["iat"] = math.floor(time.time())
    jwetoken = jwe.JWE(
        json_encode(payload),
        json_encode({"alg": "dir", "enc": enc}),
        recipient=key,
    )
    return jwetoken.serialize(compact=True)
