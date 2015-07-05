# -*- coding: utf-8 -*-
'''
tests.test_atomic
'''

import multiprocessing
import threading
import ctypes

import pytest

import atomos.atomic
import atomos.multiprocessing.atomic


refs = [(atomos.atomic.AtomicReference({}), threading.Thread),
        (atomos.multiprocessing.atomic.AtomicReference({}),
         multiprocessing.Process)]


class TestNumberT(atomos.atomic.AtomicNumber):
    def __init__(self, value=0):
        super(TestNumberT, self).__init__()
        self._value = value


class TestNumberP(atomos.multiprocessing.atomic.AtomicNumber):
    def __init__(self, value=0):
        super(TestNumberP, self).__init__(typecode_or_type=ctypes.c_int,
                                          value=value)
        self._value = value


numbers = [(TestNumberT(), threading.Thread),
           (TestNumberP(), multiprocessing.Process)]


ints = [(atomos.atomic.AtomicInteger(), threading.Thread),
        (atomos.multiprocessing.atomic.AtomicInteger(),
         multiprocessing.Process)]


@pytest.fixture(params=refs)
def atomic_reference(request):
    atomic_ref, _ = request.param
    atomic_ref.set({})
    return request.param


@pytest.fixture(params=numbers)
def atomic_number(request):
    atomic_number, _ = request.param
    atomic_number.set(0)
    return request.param


@pytest.fixture(params=ints)
def atomic_int(request):
    atomic_int, _ = request.param
    atomic_int.set(0)
    return request.param


def test_atomic_reference_get(atomic_reference):
    atomic_reference, _ = atomic_reference
    assert atomic_reference.get() == {}


def test_atomic_reference_set(atomic_reference):
    atomic_reference, _ = atomic_reference
    atomic_reference.set({'foo': 'bar'})
    assert atomic_reference.get() == {'foo': 'bar'}


def test_atomic_reference_get_and_set(atomic_reference):
    atomic_reference, _ = atomic_reference
    ret = atomic_reference.get_and_set({'foo': 'bar'})
    assert atomic_reference.get() == {'foo': 'bar'}
    assert ret == {}


def test_atomic_reference_compare_and_set(atomic_reference):
    atomic_reference, _ = atomic_reference
    assert atomic_reference.compare_and_set({}, {'foo': 'bar'}) is True
    assert atomic_reference.compare_and_set({}, {'foo', 'bar'}) is False


def test_atomic_number_add_and_get(atomic_number):
    atomic_number, _ = atomic_number
    assert atomic_number.add_and_get(1) == 1


def test_atomic_number_get_and_add(atomic_number):
    atomic_number, _ = atomic_number
    assert atomic_number.get_and_add(1) == 0


def test_atomic_number_subtract_and_get(atomic_number):
    atomic_number, _ = atomic_number
    assert atomic_number.subtract_and_get(1) == -1


def test_atomic_number_get_and_subtract(atomic_number):
    atomic_number, _ = atomic_number
    assert atomic_number.get_and_subtract(1) == 0


def test_concurrent_atomic_int(atomic_int, proc_count=10, loop_count=1000):
    atomic_int, proc = atomic_int

    def inc_atomic_int():
        for _ in range(loop_count):
            atomic_int.add_and_get(1)

    processes = []
    for _ in range(proc_count):
        p = proc(target=inc_atomic_int)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    assert atomic_int.get() == proc_count * loop_count


def test_concurrent_atomic_ref(atomic_reference,
                               proc_count=10,
                               loop_count=1000):
    atomic_reference, proc = atomic_reference
    atomic_reference.set({'count': 0})
    assert atomic_reference.get() == {'count': 0}

    def update(d):
        # N.B. A mutable object should be copied such that the update function
        # does not change the original object in memory. Failure to do so will
        # cause unexpected results!
        d = d.copy()
        d['count'] += 1
        return d

    def inc_atomic_ref():
        for _ in range(loop_count):
            while True:
                oldval = atomic_reference.get()
                newval = update(oldval)
                is_set = atomic_reference.compare_and_set(oldval, newval)
                if is_set:
                    break

    processes = []
    for _ in range(proc_count):
        p = proc(target=inc_atomic_ref)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    assert atomic_reference.get()['count'] == proc_count * loop_count
