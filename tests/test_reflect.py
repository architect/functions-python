# -*- coding: utf-8 -*-
import arc


def test_arc_reflect(arc_reflection):
    arc_reflection(params={"foo/bar": "this is it!"})
    val = arc.reflect()
    assert val == {"foo": {"bar": "this is it!"}}
