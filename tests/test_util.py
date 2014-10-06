# -*- coding: utf-8 -*-
'''
tests.test_util
'''

import threading

import atomos.util


def test_synchronized(thread_count=10, loop_count=1000):
    class SharedInt(object):
        value = 0

    shared_int = SharedInt()

    def inc(n):
        return n + 1

    @atomos.util.synchronized
    def inc_shared_int():
        for _ in range(loop_count):
            shared_int.value = inc(shared_int.value)

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=inc_shared_int)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert shared_int.value == thread_count * loop_count


def test_readers_writer_lock(acquire_shared_count=10):
    lock = atomos.util.ReadersWriterLock()

    for _ in range(acquire_shared_count):
        lock.shared.acquire()

    assert lock._reader_count == acquire_shared_count

    # Cannot acquire an exclusive lock with active readers.
    t = threading.Thread(target=lock.exclusive.acquire)
    t.start()

    t.join(1.0)

    assert t.is_alive() is True

    for _ in range(acquire_shared_count):
        lock.shared.release()

    assert lock._reader_count == 0

    t.join()

    assert t.is_alive() is False

    # Cannot acquire an exclusive lock with an active writer. (This was
    # acquired in the above thread.
    t = threading.Thread(target=lock.exclusive.acquire)
    t.start()

    t.join(1.0)

    assert t.is_alive() is True

    # Release the original acquisition.
    lock.exclusive.release()

    t.join()

    assert t.is_alive() is False

    # Cannot acquire a shared lock with an active writer. (This was acquired
    # in the above thread.)
    t = threading.Thread(target=lock.shared.acquire)
    t.start()

    t.join(1.0)

    assert t.is_alive() is True

    lock.exclusive.release()

    t.join()

    assert t.is_alive() is False
    assert lock._reader_count == 1
