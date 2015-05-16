# -*- coding: utf-8 -*-
'''
tests.test_atom
'''

import multiprocessing
import threading

import pytest

import atomos.atom
import atomos.multiprocessing.atom


atoms = [(atomos.atom.Atom({}), threading.Thread),
         (atomos.multiprocessing.atom.Atom({}), multiprocessing.Process)]


@pytest.fixture(params=atoms)
def atom(request):
    return request.param


def test_atom_deref(atom):
    atom, _ = atom
    assert atom.deref() == {}


def test_atom_swap(atom):
    atom, _ = atom
    def update_state(cur_state, k, v):
        cur_state = cur_state.copy()
        cur_state[k] = v
        return cur_state

    atom.swap(update_state, 'foo', 'bar')
    assert atom.deref() == {'foo': 'bar'}


def test_atom_reset(atom):
    atom, _ = atom
    atom.reset('foo')
    assert atom.deref() == 'foo'


def test_atom_compare_and_set(atom):
    atom, _ = atom
    atom.reset('foo')

    assert atom.compare_and_set('foo', 'bar') is True
    assert atom.compare_and_set('foo', 'bar') is False


def test_concurrent_swap(atom, proc_count=10, loop_count=1000):
    atom, proc = atom
    atom.reset(0)

    def inc_for_loop_count():
        for _ in range(loop_count):
            atom.swap(lambda n: n + 1)

    processes = []
    for _ in range(proc_count):
        p = proc(target=inc_for_loop_count)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    assert atom.deref() == proc_count * loop_count


def test_concurrent_compare_and_set(atom, proc_count=10, loop_count=1000):
    atom, proc = atom
    atom.reset(0)

    successes = multiprocessing.Value('i', 0)
    def attempt_inc_for_loop_count(successes):
        for _ in range(loop_count):
            oldval = atom.deref()
            newval = oldval + 1
            if atom.compare_and_set(oldval, newval):
                with successes.get_lock():
                    successes.value += 1

    processes = []
    for _ in range(proc_count):
        p = proc(target=attempt_inc_for_loop_count, args=(successes,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    assert atom.deref() == successes.value
