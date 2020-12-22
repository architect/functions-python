import os
from .session.cookies import _write_cookie, _read_cookie
from .session.jwe import jwe_read, jwe_write
from .session.ddb import ddb_read, ddb_write

COOKIE_NAME: str = "_idx"
DEFAULT_SESSION_TABLE: str = "arc-sessions"


def session_read(req):
    table_name = os.environ.get("SESSION_TABLE_NAME", DEFAULT_SESSION_TABLE)
    try:
        cookie = _read_cookie(req, COOKIE_NAME)
        return jwe_read(cookie) if table_name == "jwe" else ddb_read(cookie, table_name)
    except:
        return {}


def session_write(payload):
    table_name = os.environ.get("SESSION_TABLE_NAME", DEFAULT_SESSION_TABLE)
    cookie = (
        jwe_write(payload) if table_name == "jwe" else ddb_write(payload, table_name)
    )
    return _write_cookie(cookie, COOKIE_NAME)
