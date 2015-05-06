# -*- coding: utf-8 -*-
'''
tests.test_atomic
'''

import threading

import pytest

import atomos.atomic


@pytest.fixture
def atomic_reference():
    return atomos.atomic.AtomicReference({})


@pytest.fixture
def atomic_number():
    class TestNumber(atomos.atomic.AtomicNumber):
        def __init__(self, value=0):
            super(TestNumber, self).__init__()
            self._value = value

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


def test_concurrent_atomic_int(thread_count=10, loop_count=1000):
    atomic_int = atomos.atomic.AtomicInteger()

    def inc_atomic_int():
        for _ in range(loop_count):
            atomic_int.add_and_get(1)

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=inc_atomic_int)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert atomic_int.get() == thread_count * loop_count


def test_concurrent_atomic_ref(thread_count=10, loop_count=10000):
    atomic_ref = atomos.atomic.AtomicReference({'count': 0})
    assert atomic_ref.get() == {'count': 0}

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
                oldval = atomic_ref.get()
                newval = update(oldval)
                is_set = atomic_ref.compare_and_set(oldval, newval)
                if is_set:
                    break

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=inc_atomic_ref)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert atomic_ref.get()['count'] == thread_count * loop_count
