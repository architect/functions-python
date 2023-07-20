import os
import simplejson as _json
from datetime import datetime, timedelta
from base64 import b64encode, urlsafe_b64encode
from typing import Any, Dict, Tuple, Optional
from cryptography.hazmat.primitives import hashes, hmac
from arc.tables import table


def _get_secret() -> str:
    return os.environ.get("ARC_APP_SECRET", os.environ.get("ARC_APP_NAME", "fallback"))


def _sign(value: str, secret: str) -> str:
    h = hmac.HMAC(secret.encode("utf-8"), hashes.SHA256())
    h.update(value.encode("utf-8"))
    digest = b64encode(h.finalize()).decode("utf-8").rstrip("=")
    return value + "." + digest


def _unsign(value: str, secret: str) -> Tuple[str, bool]:
    where = value.rfind(".")
    before, after = value[:where], value[where + 1 :]
    return (before, _sign(before, secret) == value)


def _week_from_now() -> int:
    return int((datetime.now() + timedelta(weeks=1)).timestamp())


def _uid_safe(byte_length: int) -> str:
    buff = os.urandom(byte_length)
    return urlsafe_b64encode(buff).decode("utf-8").rstrip("=")


def ddb_read(cookie: Optional[str], table_name: str) -> Dict[Any, Any]:
    db = table(table_name)

    if cookie is not None:
        secret = _get_secret()
        cookie, valid = _unsign(cookie, secret)
        if not valid:
            cookie = None

    # create a new session
    if cookie is None:
        session = {
            "_idx": _uid_safe(18),
            "_secret": _uid_safe(18),
            "_ttl": _week_from_now(),
        }
        db.put_item(Item=session)
        return session

    result = db.get_item(Key={"_idx": cookie}, ConsistentRead=True)
    item = result.get("Item", {})
    session = _json.loads(_json.dumps(item))
    return session


def ddb_write(payload: Dict[Any, Any], table_name: str) -> str:
    payload = dict(payload)
    payload["_ttl"] = _week_from_now()

    db = table(table_name)
    db.put_item(Item=payload)

    secret = _get_secret()
    return _sign(payload.get("_idx"), secret)
