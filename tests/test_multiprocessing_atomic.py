# -*- coding: utf-8 -*-
'''
tests.test_atomic
'''

from multiprocessing import Process

import pytest

import atomos.multiprocessing.atomic


@pytest.fixture
def atomic_reference():
    return atomos.multiprocessing.atomic.AtomicReference({})


@pytest.fixture
def atomic_number():
    class TestNumber(atomos.multiprocessing.atomic.AtomicNumber):
        def __init__(self, value=0):
            super(TestNumber, self).__init__(typecode_or_type='i', value=value)

    return TestNumber()


def test_atomic_reference_get(atomic_reference):
    assert atomic_reference.get() == {}


def test_atomic_reference_set(atomic_reference):
    atomic_reference.set({'foo': 'bar'})

    assert atomic_reference.get() == {'foo': 'bar'}


def test_atomic_reference_get_and_set(atomic_reference):
    ret = atomic_reference.get_and_set({'foo': 'bar'})

    assert atomic_reference.get() == {'foo': 'bar'}
    assert ret == {}


def test_atomic_reference_compare_and_set(atomic_reference):
    assert atomic_reference.compare_and_set({}, {'foo': 'bar'}) is True
    assert atomic_reference.compare_and_set({}, {'foo', 'bar'}) is False


def test_atomic_number_add_and_get(atomic_number):
    assert atomic_number.add_and_get(1) == 1


def test_atomic_number_get_and_add(atomic_number):
    assert atomic_number.get_and_add(1) == 0


def test_atomic_number_subtract_and_get(atomic_number):
    assert atomic_number.subtract_and_get(1) == -1


def test_atomic_number_get_and_subtract(atomic_number):
    assert atomic_number.get_and_subtract(1) == 0


def test_concurrent_atomic_int(process_count=10, loop_count=1000):
    atomic_int = atomos.multiprocessing.atomic.AtomicInteger()

    def inc_atomic_int():
        for _ in range(loop_count):
            atomic_int.add_and_get(1)

    processes = []
    for _ in range(process_count):
        p = Process(target=inc_atomic_int)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    assert atomic_int.get() == process_count * loop_count
