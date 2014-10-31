# -*- coding: utf-8 -*-
'''
atomos.atomic

Atomic primitives.
'''

import types

import atomos.util as util


class AtomicReference(object):
    '''
    A reference to an object which allows atomic manipulation semantics.

    AtomicReferences are particularlly useful when an object cannot otherwise
    be manipulated atomically.
    '''
    def __init__(self, value=None):
        self._value = value
        self._lock = util.ReadersWriterLock()

    def __repr__(self):
        return util.repr(__name__, self, self._value)

    def get(self):
        '''
        Returns the value.
        '''
        with self._lock.shared:
            return self._value

    def set(self, value):
        '''
        Atomically sets the value to `value`.

        :param value: The value to set.
        '''
        with self._lock.exclusive:
            self._value = value
            return value

    def get_and_set(self, value):
        '''
        Atomically sets the value to `value` and returns the old value.

        :param value: The value to set.
        '''
        with self._lock.exclusive:
            oldval = self._value
            self._value = value
            return oldval

    def compare_and_set(self, expect, update):
        '''
        Atomically sets the value to `update` if the current value is equal to
        `expect`.

        :param expect: The expected current value.
        :param update: The value to set if and only if `expect` equals the
        current value.
        '''
        with self._lock.exclusive:
            if self._value == expect:
                self._value = update
                return True

            return False


class AtomicBoolean(AtomicReference):
    '''
    A boolean value whichs allows atomic manipulation semantics.
    '''
    def __init__(self, value=False):
        super(AtomicBoolean, self).__init__(value=value)

    # We do not need a locked get since a boolean is not a complex data type.
    def get(self):
        '''
        Returns the value.
        '''
        return self._value

    def __setattr__(self, name, value):
        # Ensure the `value` attribute is always a bool.
        if name == '_value' and not isinstance(value, types.BooleanType):
            raise TypeError('_value must be of type bool')

        super(AtomicBoolean, self).__setattr__(name, value)


class AtomicNumber(AtomicReference):
    '''
    AtomicNumber object super type.

    Contains common methods for AtomicInteger, AtomicLong, and AtomicFloat.
    '''
    # We do not need a locked get since numbers are not complex data types.
    def get(self):
        '''
        Returns the value.
        '''
        return self._value

    def add_and_get(self, delta):
        '''
        Atomically adds `delta` to the current value.

        :param delta: The delta to add.
        '''
        with self._lock.exclusive:
            self._value += delta
            return self._value

    def get_and_add(self, delta):
        '''
        Atomically adds `delta` to the current value and returns the old value.

        :param delta: The delta to add.
        '''
        with self._lock.exclusive:
            oldval = self._value
            self._value += delta
            return oldval

    def subtract_and_get(self, delta):
        '''
        Atomically subtracts `delta` from the current value.

        :param delta: The delta to subtract.
        '''
        with self._lock.exclusive:
            self._value -= delta
            return self._value

    def get_and_subtract(self, delta):
        '''
        Atomically subtracts `delta` from the current value and returns the
        old value.

        :param delta: The delta to subtract.
        '''
        with self._lock.exclusive:
            oldval = self._value
            self._value -= delta
            return oldval


class AtomicInteger(AtomicNumber):
    '''
    An integer value which allows atomic manipulation semantics.
    '''
    def __init__(self, value=0):
        super(AtomicInteger, self).__init__(value=value)

    def __setattr__(self, name, value):
        # Ensure the `_value` attribute is always an int.
        if name == '_value' and not isinstance(value, types.IntType):
            raise TypeError('_value must be of type int')

        super(AtomicInteger, self).__setattr__(name, value)


class AtomicLong(AtomicNumber):
    '''
    A long value which allows atomic manipulation semantics.
    '''
    def __init__(self, value=long(0)):
        super(AtomicLong, self).__init__(value=value)

    def __setattr__(self, name, value):
        # Ensure the `_value` attribute is always a long.
        if name == '_value' and not isinstance(value, types.LongType):
            raise TypeError('_value must be of type long')

        super(AtomicLong, self).__setattr__(name, value)


class AtomicFloat(AtomicNumber):
    '''
    A float value which allows atomic manipulation semantics.
    '''
    def __init__(self, value=float(0)):
        super(AtomicFloat, self).__init__(value=value)

    def __setattr__(self, name, value):
        # Ensure the `_value` attribute is always a float.
        if name == '_value' and not isinstance(value, types.FloatType):
            raise TypeError('_value must be of type float')

        super(AtomicFloat, self).__setattr__(name, value)
