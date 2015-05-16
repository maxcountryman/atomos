# -*- coding: utf-8 -*-
'''
atomos.multiprocessing.atomic

Atomic primitives multiprocessing.
'''

import types
import ctypes
import multiprocessing
import multiprocessing.managers

import six

import atomos.util as util
import atomos.atomic as atomic

if six.PY3:
    long = int


class _AtomicReference(atomic.AtomicReference):
    '''
    A reference to an object which allows atomic manipulation semantics.

    AtomicReferences are particularlly useful when an object cannot otherwise
    be manipulated atomically.
    '''
    def __init__(self, value=None):
        super(_AtomicReference, self).__init__(value=value)
        self._lock = util.ReadersWriterLockMultiprocessing()

    def __repr__(self):
        return util.repr(__name__, self, self._value)

    def _proxy_value(self):
        return self._value


class AtomicManager(multiprocessing.managers.BaseManager):
    pass


AtomicManager.register('AtomicReference',
                       _AtomicReference,
                       exposed=['get',
                                'set',
                                'get_and_set',
                                'compare_and_set',
                                '_proxy_value',
                                '__repr__'])

# HACK: This is a bit of a hack. Essentially we need to run a manager which
# specifically exposes the multiprocessing version of AtomicReference. If we
# don't do this then memory cannot be shared between processes.
_started = False
if not _started:
    _manager = AtomicManager()
    _manager.start()
    AtomicReference = _manager.AtomicReference
    _started = True


class AtomicCtypesReference(object):
    '''
    A reference to an object which allows atomic manipulation semantics.

    AtomicCtypesReferences are particularlly useful when an object cannot
    otherwise be manipulated atomically.

    This only support ctypes data types.
    https://docs.python.org/3.4/library/ctypes.html#fundamental-data-types
    '''
    def __init__(self, typecode_or_type=None, value=None):
        '''
        Atomic reference

        :param typecode_or_type: The type of object allocated from shared
            memory.
        :param value: The default value.
        '''
        self._typecode_or_type = typecode_or_type
        self._reference = multiprocessing.Value(self._typecode_or_type, value)

    def __repr__(self):
        return util.repr(__name__, self, self._reference)

    def get(self):
        '''
        Returns the value.
        '''
        with self._reference.get_lock():
            return self._reference.value

    def set(self, value):
        '''
        Atomically sets the value to `value`.

        :param value: The value to set.
        '''
        with self._reference.get_lock():
            self._reference.value = value
            return value

    def get_and_set(self, value):
        '''
        Atomically sets the value to `value` and returns the old value.

        :param value: The value to set.
        '''
        with self._reference.get_lock():
            oldval = self._reference.value
            self._reference.value = value
            return oldval

    def compare_and_set(self, expect, update):
        '''
        Atomically sets the value to `update` if the current value is equal to
        `expect`.

        :param expect: The expected current value.
        :param update: The value to set if and only if `expect` equals the
        current value.
        '''
        with self._reference.get_lock():
            if self._reference.value == expect:
                self._reference.value = update
                return True

            return False


class AtomicBoolean(AtomicCtypesReference):
    '''
    A boolean value whichs allows atomic manipulation semantics.
    '''
    def __init__(self, value=False):
        super(AtomicBoolean, self).__init__(typecode_or_type=ctypes.c_bool,
                                            value=value)

    # We do not need a locked get since a boolean is not a complex data type.
    def get(self):
        '''
        Returns the value.
        '''
        return self._reference.value

    def __setattr__(self, name, value):
        # Ensure the `value` attribute is always a bool.
        if name == '_value' and not isinstance(value, types.BooleanType):
            raise TypeError('_value must be of type bool')

        super(AtomicBoolean, self).__setattr__(name, value)


class AtomicNumber(AtomicCtypesReference):
    '''
    AtomicNumber object super type.

    Contains common methods for AtomicInteger, AtomicLong, and AtomicFloat.
    '''
    # We do not need a locked get since numbers are not complex data types.
    def get(self):
        '''
        Returns the value.
        '''
        return self._reference.value

    def add_and_get(self, delta):
        '''
        Atomically adds `delta` to the current value.

        :param delta: The delta to add.
        '''
        with self._reference.get_lock():
            self._reference.value += delta
            return self._reference.value

    def get_and_add(self, delta):
        '''
        Atomically adds `delta` to the current value and returns the old value.

        :param delta: The delta to add.
        '''
        with self._reference.get_lock():
            oldval = self._reference.value
            self._reference.value += delta
            return oldval

    def subtract_and_get(self, delta):
        '''
        Atomically subtracts `delta` from the current value.

        :param delta: The delta to subtract.
        '''
        with self._reference.get_lock():
            self._reference.value -= delta
            return self._reference.value

    def get_and_subtract(self, delta):
        '''
        Atomically subtracts `delta` from the current value and returns the
        old value.

        :param delta: The delta to subtract.
        '''
        with self._reference.get_lock():
            oldval = self._reference.value
            self._reference.value -= delta
            return oldval


class AtomicInteger(AtomicNumber):
    '''
    An integer value which allows atomic manipulation semantics.
    '''
    def __init__(self, value=0):
        super(AtomicInteger, self).__init__(typecode_or_type=ctypes.c_int,
                                            value=value)

    def __setattr__(self, name, value):
        # Ensure the `_value` attribute is always an int.
        if name == '_value' and not isinstance(value, int):
            raise TypeError('_value must be of type int')

        super(AtomicInteger, self).__setattr__(name, value)


class AtomicLong(AtomicNumber):
    '''
    A long value which allows atomic manipulation semantics.
    '''
    def __init__(self, value=long(0)):
        super(AtomicLong, self).__init__(typecode_or_type=ctypes.c_long,
                                         value=value)

    def __setattr__(self, name, value):
        # Ensure the `_value` attribute is always a long.
        if name == '_value' and not isinstance(value, long):
            raise TypeError('_value must be of type long')

        super(AtomicLong, self).__setattr__(name, value)


class AtomicFloat(AtomicNumber):
    '''
    A float value which allows atomic manipulation semantics.
    '''
    def __init__(self, value=float(0)):
        super(AtomicFloat, self).__init__(typecode_or_type=ctypes.c_float,
                                          value=value)

    def __setattr__(self, name, value):
        # Ensure the `_value` attribute is always a float.
        if name == '_value' and not isinstance(value, float):
            raise TypeError('_value must be of type float')

        super(AtomicFloat, self).__setattr__(name, value)
