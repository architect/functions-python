import os
from .session.cookies import _write_cookie, _read_cookie
from .session.jwe import jwe_read, jwe_write

COOKIE_NAME: str = "_idx"


def session_read(req):
    if os.environ.get("SESSION_TABLE_NAME") == "jwe":
        try:
            cookie = _read_cookie(req, COOKIE_NAME)
            return jwe_read(cookie)
        except:
            return {}

    raise NotImplementedError()


def session_write(payload):
    if os.environ.get("SESSION_TABLE_NAME") == "jwe":
        cookie = jwe_write(payload)
        return _write_cookie(cookie, COOKIE_NAME)

    raise NotImplementedError()
