import os
from .cookies import _write_cookie, _read_cookie
from .jwe import jwe_read, jwe_write
from .ddb import ddb_read, ddb_write

COOKIE_NAME: str = "_idx"


def _get_table_name():
    table_name = os.environ.get(
        "ARC_SESSION_TABLE_NAME", os.environ.get("SESSION_TABLE_NAME")
    )
    if not table_name:
        raise TypeError(
            "To use sessions, ensure the table name is specified in the ARC_SESSION_TABLE_NAME env vars"
        )
    return table_name


def session_read(req):
    table_name = _get_table_name()
    try:
        cookie = _read_cookie(req, COOKIE_NAME)
        if table_name == "jwe":
            return jwe_read(cookie)
        else:
            return ddb_read(cookie, table_name)
    except:
        return {}


def session_write(payload):
    table_name = _get_table_name()
    if table_name == "jwe":
        cookie = jwe_write(payload)
    else:
        cookie = ddb_write(payload, table_name)
    return _write_cookie(cookie, COOKIE_NAME)
