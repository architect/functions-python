import json
import math
import os
import time
from typing import Any, Dict

from jose import jwe

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

    _key = secret


def jwe_read(cookie: str) -> Dict[Any, Any]:
    _setup_crypto()
    result = jwe.decrypt(cookie, _key)
    return json.loads(result)


def jwe_write(payload: Dict[Any, Any]) -> str:
    _setup_crypto()
    payload = dict(payload)
    payload["iat"] = math.floor(time.time())
    jwetoken = jwe.encrypt(json.dumps(payload), _key, algorithm="dir", encryption=_enc)
    return jwetoken.decode("utf-8")
