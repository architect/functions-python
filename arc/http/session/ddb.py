import hmac
import hashlib
import os
import urllib.parse
import simplejson as _json
from datetime import datetime, timedelta
from base64 import b64encode, urlsafe_b64encode
from typing import Any, Dict, Tuple, Optional
from arc.tables import table


def _get_secret() -> str:
    return os.environ.get("ARC_APP_SECRET", os.environ.get("ARC_APP_NAME", "fallback"))


def _sign(value: str, secret: str) -> str:
    key = str.encode(secret)
    msg = str.encode(value)
    h = hmac.new(key, msg=msg, digestmod=hashlib.sha256)
    digest = b64encode(h.digest()).decode("utf-8").rstrip("=")
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
        if "%" in cookie:
            cookie = urllib.parse.unquote(cookie)
        secret = _get_secret()
        cookie, valid = _unsign(cookie, secret)
        if not valid:
            cookie = None

    # Create a new session
    def create():
        session = {
            "_idx": _uid_safe(18),
            "_secret": _uid_safe(18),
            "_ttl": _week_from_now(),
        }
        db.put_item(Item=session)
        return session

    # User has no session, so create it
    if cookie is None:
        return create()

    result = db.get_item(Key={"_idx": cookie}, ConsistentRead=True)
    item = result.get("Item")

    # User session not found in the database, so create it
    if not item:
        return create()

    session = _json.loads(_json.dumps(item))
    return session


def ddb_write(payload: Dict[Any, Any], table_name: str) -> str:
    payload = dict(payload)
    payload["_ttl"] = _week_from_now()

    db = table(table_name)
    db.put_item(Item=payload)

    secret = _get_secret()
    return _sign(payload.get("_idx"), secret)
