import os
from arc.services import _services
from .cookies import _write_cookie, _read_cookie
from .jwe import jwe_read, jwe_write
from .ddb import ddb_read, ddb_write

_session_table_cache = None


def _get_session_table():
    global _session_table_cache

    testing = os.environ.get("_TESTING")
    if _session_table_cache and not testing:
        return _session_table_cache

    table_name = os.environ.get(
        "ARC_SESSION_TABLE_NAME", os.environ.get("SESSION_TABLE_NAME")
    )
    if not table_name:
        raise TypeError(
            "To use sessions, ensure the session table name is specified in your ARC_SESSION_TABLE_NAME env var"
        )
    service_map = _services()
    tables = service_map.get("tables", {})
    # Tables services: key would be logical table name, value would be physical
    # Providing a physical table name is more legacy Node.js @architect/functions behavior, whereas this client requires the logical name
    # Still, we want to interop, so denormalize to make it happen
    if tables.get(table_name):
        _session_table_cache = table_name
    if not _session_table_cache and table_name in tables.values():
        _session_table_cache = list(filter(lambda i: tables[i] == table_name, tables))[
            0
        ]
    if not _session_table_cache:
        raise TypeError(f"Session table name '{table_name}' could not be found")


def session_read(req):
    is_jwe = (
        os.environ.get("ARC_SESSION_TABLE_NAME", os.environ.get("SESSION_TABLE_NAME"))
        == "jwe"
    )
    try:
        cookie = _read_cookie(req)
        if is_jwe:
            return jwe_read(cookie)
        else:
            _get_session_table()
            return ddb_read(cookie, _session_table_cache)
    except:
        return {}


def session_write(payload):
    is_jwe = (
        os.environ.get("ARC_SESSION_TABLE_NAME", os.environ.get("SESSION_TABLE_NAME"))
        == "jwe"
    )
    if is_jwe:
        cookie = jwe_write(payload)
    else:
        _get_session_table()
        cookie = ddb_write(payload, _session_table_cache)
    return _write_cookie(cookie)
