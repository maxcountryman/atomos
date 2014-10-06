# -*- coding: utf-8 -*-
'''
tests.test_aref
'''

import pytest

import atomos.atom


@pytest.fixture
def aref():
    return atomos.atom.ARef()


def test_aref_get_watches(aref):
    assert aref.get_watches() == {}


def test_aref_add_watch(aref):
    def watch(k, ref, old, new):
        pass

    aref.add_watch('foo', watch)

    assert 'foo' in aref.get_watches()
    assert watch in aref.get_watches().itervalues()


def test_aref_remove_watch(aref):
    def watch(k, ref, old, new):
        pass

    aref.add_watch('foo', watch)
    aref.remove_watch('foo')

    assert 'foo' not in aref.get_watches()
    assert watch not in aref.get_watches().itervalues()


def test_aref_notify_watches(aref):
    watches = ['foo', 'bar', 'baz']
    watched = {}

    def watch(k, ref, old, new):
        watched[k] = {'old': old, 'new': new, 'ref': ref}

    for k in watches:
        aref.add_watch(k, watch)

    old, new = 'a', 'b'
    aref.notify_watches(old, new)

    for k in watches:
        assert k in watched
        assert watched[k] == {'old': old, 'new': new, 'ref': aref}
