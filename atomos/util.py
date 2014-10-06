# -*- coding: utf-8 -*-
'''
atomos.util

Utility functions.
'''

import functools
import threading


def repr(module, instance, value):
    repr_fmt = '<{m}.{cls}({val}) object at {addr}>'
    return repr_fmt.format(m=module,
                           cls=instance.__class__.__name__,
                           val=value,
                           addr=hex(id(instance)))


def synchronized(fn):
    '''
    A decorator which acquires a lock before attempting to execute its wrapped
    function. Releases the lock in a finally clause.

    :param fn: The function to wrap.
    '''
    lock = threading.Lock()

    @functools.wraps(fn)
    def decorated(*args, **kwargs):
        lock.acquire()
        try:
            return fn(*args, **kwargs)
        finally:
            lock.release()

    return decorated


class ReadersWriterLock(object):
    '''
    A readers-writer lock.

    Provides exclusive locking on write while allowing for concurrent access
    on read. Useful for when a data structure cannot be updated atomically and
    therefore reads during a write could yield incorrect representations.

    To use, construct a new `ReadersWriterLock` instance. Use the shared
    property (i.e. the shared lock object) when the shared semantic is desired
    and the exclusive property (i.e. the exclusive lock object) when the
    exclusive semantic is desired.

    Lock objects are wrappers around `threading.Lock`. As a result, the normal
    usage patterns are valid. For example, a shared lock can be acquired like
    this::

        >>> lock = ReadersWriterLock()
        >>> lock.shared.acquire()

    An exclusive lock can be acquired in a similar fashion, using the
    `exclusive` attribute instead. Both locks are also provisioned as context
    managers. Note that a difference in API here is that no blocking parameter
    should be provided.

    Readers-writer locks are meant to allow for a specific situation where a
    critical section should be visible to multiple readers so long as there is
    no writer. The latter case is simply an exclusive lock. However this does
    not allow for concurrent readers.

    To facilitate multiple readers, two "locks" are provided: a shared and
    exclusive lock. While the exclusive lock is not held, the shared lock may
    be acquired as many times as desired. However once the exclusive lock is
    obtained, attempts to acquire the read lock will block until the exclusive
    lock is released.

    Note that obtaining the write lock implies that there are no readers and in
    fact an attempt to acquire it will block until all the readers have
    released the lock.
    '''
    def __init__(self):
        self._reader_lock = threading.Lock()
        self._writer_lock = threading.Lock()
        self._reader_count = 0

        class SharedLock(object):
            def acquire(inner):
                '''
                Acquires the shared lock, prevents acquisition of the exclusive
                lock.
                '''
                self._reader_lock.acquire()

                if self._reader_count == 0:
                    self._writer_lock.acquire()

                try:
                    self._reader_count += 1
                finally:
                    self._reader_lock.release()

            def release(inner):
                '''
                Releases the shared lock, allows acquisition of the exclusive
                lock.
                '''
                self._reader_lock.acquire()

                try:
                    self._reader_count -= 1
                finally:
                    if self._reader_count == 0:
                        self._writer_lock.release()

                    self._reader_lock.release()

            def __enter__(inner):
                inner.acquire()
                return inner

            def __exit__(inner, exc_value, exc_type, tb):
                inner.release()

        self.shared = SharedLock()

        class ExclusiveLock(object):
            def acquire(inner):
                '''
                Acquires the exclusive lock, prevents acquisition of the shared
                lock.
                '''
                self._writer_lock.acquire()

            def release(inner):
                '''
                Releases the exclusive lock, allows acquistion of the shared
                lock.
                '''
                self._writer_lock.release()

            def __enter__(inner):
                inner.acquire()
                return inner

            def __exit__(inner, exc_value, exc_type, tb):
                inner.release()

        self.exclusive = ExclusiveLock()
