# -*- coding: utf-8 -*-
'''
tests.test_atom
'''

import threading

import pytest

import atomos.atom


@pytest.fixture
def atom():
    return atomos.atom.Atom({})


def test_atom_deref(atom):
    assert atom.deref() == {}


def test_atom_swap(atom):
    def update_state(cur_state, k, v):
        cur_state[k] = v
        return cur_state

    atom.swap(update_state, 'foo', 'bar')

    assert atom.deref() == {'foo': 'bar'}


def test_atom_reset(atom):
    atom.reset('foo')

    assert atom.deref() == 'foo'


def test_atom_compare_and_set(atom):
    atom.reset('foo')

    assert atom.compare_and_set('foo', 'bar') is True
    assert atom.compare_and_set('foo', 'bar') is False


def test_concurrent_swap(atom, thread_count=10, loop_count=1000):
    atom.reset(0)

    def inc_for_loop_count():
        for _ in range(loop_count):
            atom.swap(lambda n: n + 1)

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=inc_for_loop_count)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert atom.deref() == thread_count * loop_count


def test_concurrent_compare_and_set(atom, thread_count=10, loop_count=1000):
    atom.reset(0)

    successes = []
    def attempt_inc_for_loop_count():
        for _ in range(loop_count):
            oldval = atom.deref()
            newval = oldval + 1
            ret = atom.compare_and_set(oldval, newval)
            if ret:
                successes.append(True)

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=attempt_inc_for_loop_count)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert atom.deref() == len(successes)
