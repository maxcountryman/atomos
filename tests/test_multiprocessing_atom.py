# -*- coding: utf-8 -*-
'''
tests.test_multiprocessing_atomic
'''

import multiprocessing

import pytest

import atomos.multiprocessing.atom


@pytest.fixture
def atom():
    return atomos.multiprocessing.atom.Atom({})


def test_atom_deref(atom):
    return atom.deref() == {}


def test_atom_swap(atom):
    def update_state(cur_state, k, v):
        cur_state = cur_state.copy()
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


def test_parallel_swap(atom, process_count=10, loop_count=1000):
    atom.reset(0)

    def inc_for_loop_count():
        for _ in range(loop_count):
            atom.swap(lambda n: n + 1)

    processes = []
    for _ in range(process_count):
        p = multiprocessing.Process(target=inc_for_loop_count)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    assert atom.deref() == process_count * loop_count
