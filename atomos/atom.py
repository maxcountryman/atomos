# -*- coding: utf-8 -*-
'''
atomos.atom

Atom data type.
'''

import collections

import atomos.atomic as atomic
import atomos.util as util


class ARef(object):
    '''
    Ref object super type.

    Refs may hold watches which can be notified when a value a ref holds
    changes. In effect, a watch is a callback which receives the key,
    object reference, oldval, and newval.

    For example, a watch function could be constructed like this::

        >>> def watch(k, ref, old, new):
        ...     print k, ref, old, new
        >>> aref = ARef()
        >>> aref.add_watch(watch)

    However note that `ARef` should generally be subclassed, a la `Atom`, as it
    does not independently hold any value and functions merely as a container
    for the watch semantics.
    '''
    def __init__(self):
        self._watches = {}

    def get_watches(self):
        '''
        Returns the watches dictionary.
        '''
        return self._watches

    @util.synchronized
    def add_watch(self, key, fn):
        '''
        Adds `key` to the watches dictionary with the value `fn`.

        :param key: The key for this watch.
        :param fn: The value for this watch, should be a function. Note that
        this function will be passed values which should not be mutated wihtout
        copying as other watches may in turn be passed the same reference!
        '''
        self._watches[key] = fn

    @util.synchronized
    def remove_watch(self, key):
        '''
        Removes `key` from the watches dictionary.

        :param key: The key of the watch to remove.
        '''
        self._watches.pop(key, None)

    def notify_watches(self, oldval, newval):
        '''
        Passes `oldval` and `newval` to each `fn` in the watches dictionary,
        passing along its respective key and the reference to this object.

        :param oldval: The old value which will be passed to the watch.
        :param newval: The new value which will be passed to the watch.
        '''
        watches = self._watches.copy()
        for k in watches:
            fn = watches[k]
            if isinstance(fn, collections.Callable):
                fn(k, self, oldval, newval)


class Atom(ARef):
    '''
    Atom object type.

    Atoms store mutable state and provide thread-safe methods for retrieving
    and altering it. This is useful in multi-threaded contexts or any time an
    application makes use of shared mutable state. By using an atom, it is
    possible to ensure that the read and write operations are always
    consistent.

    For example, if an application uses a dictionary to store state, using an
    atom will guarantee that the dictionary is never in an inconsistent state
    as it is being updated::

        >>> state = Atom({'active_conns': 0, 'clients': set([])})
        >>> def new_client(cur_state, client):
        ...     cur_state['clients'].add(client)
        ...     cur_state['active_conns'] += 1
        ...     return cur_state
        >>> state.swap(new_client, 'foo')

    In the above example we use an atom to store state about connections. Our
    mutation function, `new_client` is a function which takes the existing
    state contained by the atom and a new client. Any part of our program which
    reads the atom's state by using `deref` will always see a consistent view
    of its value.

    This is particularly useful when altering shared mutable state which cannot
    be changed atomically. Atoms enable atomic semantics for such objects.

    Because atoms are themselves refs and inherit from `ARef`, it is also
    possible to add watches to them. Watches can be thought of callbacks which
    are invoked when the atom's state changes.

    For example, if we would like to log each time a client connects, we can
    write a watch that will be responsible for this and then add it to the
    state atom::

        >>> state = Atom({'active_conns': 0, 'clients': set([])})
        >>> def log_new_clients(k, ref, old, new):
        ...     if not new['active_conns'] > old['active_conns']:
        ...         return
        ...     old_clients = old['clients']
        ...     new_clients = new['clients']
        ...     print 'new client', new_clients.difference(old_clients)
        >>> state.add_watch('log_new_clients', log_new_clients)

    We have added a watch which will print out a message when the client count
    has increased, i.e. a client has been added. Note that for a real world
    application, a proper logging facility should be preferred over print.

    Watches are keyed by the first value passed to `add_watch` and are invoked
    whenver the atom changes with the key, reference, old state, and new state
    as parameters.

    Note that watch functions may be called from multiple threads at once and
    therefore their ordering is not guaranteed. For instance, an atom's state
    may change, and before the watches can be notified another thread may alter
    the atom and trigger notifications. It is possible for the second thread's
    notifications to arrive before the first's.
    '''
    def __init__(self, state):
        super(Atom, self).__init__()
        self._state = atomic.AtomicReference(state)

    def __repr__(self):
        return util.repr(__name__, self, self._state._value)

    def deref(self):
        '''
        Returns the value held.
        '''
        return self._state.get()

    def swap(self, fn, *args, **kwargs):
        '''
        Given a mutator `fn`, calls `fn` with the atom's current state, `args`,
        and `kwargs`. The return value of this invocation becomes the new value
        of the atom. Returns the new value.

        :param fn: A function which will be passed the current state. Should
        return a new state. This absolutely MUST NOT mutate the reference to
        the current state! If it does, this function map loop indefinitely.
        :param \*args: Arguments to be passed to `fn`.
        :param \*\*kwargs: Keyword arguments to be passed to `fn`.
        '''
        while True:
            oldval = self.deref()
            newval = fn(oldval, *args, **kwargs)
            if self._state.compare_and_set(oldval, newval):
                self.notify_watches(oldval, newval)
                return newval

    def reset(self, newval):
        '''
        Resets the atom's value to `newval`, returning its old value.

        :param newval: The new value to set.
        '''
        oldval = self._state.get()
        self._state.set(newval)
        self.notify_watches(oldval, newval)
        return oldval

    def compare_and_set(self, oldval, newval):
        '''
        Given `oldval` and `newval`, sets the atom's value to `newval` if and
        only if `oldval` is the atom's current value. Returns `True` upon
        success, otherwise `False`.

        :param oldval: The old expected value.
        :param newval: The new value which will be set if and only if `oldval`
        equals the current value.
        '''
        ret = self._state.compare_and_set(oldval, newval)
        if ret:
            self.notify_watches(oldval, newval)

        return ret
