import os
from .session.jwe import jwe_read, jwe_write

def session_read(req):
    if os.environ.get("SESSION_TABLE_NAME") == "jwe":
        return jwe_read(req)

    raise NotImplementedError()


def session_write(payload):
    if os.environ.get("SESSION_TABLE_NAME") == "jwe":
        return jwe_write(payload)

    raise NotImplementedError()
