# -*- coding: utf-8 -*-
import arc


def test_arc_services(arc_services):
    arc_services(params={"foo/bar": "this is it!"})
    val = arc.services()
    assert val == {"foo": {"bar": "this is it!"}}
