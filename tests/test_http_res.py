# -*- coding: utf-8 -*-
import json
import arc

# TODO: implement tests when Arc's req/res fixtures can be ported to py; see: https://github.com/architect/req-res-fixtures


def test_method_exists():
    mock = {"version": "2.0", "headers": {}}
    ok = {"ok": True}
    res = arc.http.res(mock, ok)
    assert res.get("headers")
    assert res.get("statusCode") == 200
    assert res.get("body") == json.dumps(ok)
