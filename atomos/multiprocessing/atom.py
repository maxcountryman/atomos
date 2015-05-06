# -*- coding: utf-8 -*-
'''
atomos.multiprocessing.atom

Atom data type.
'''

import atomos.atom
import atomos.multiprocessing.atomic as atomic
import atomos.util as util


class Atom(atomos.atom.Atom):
    '''
    Same as atomos.atom.Atom, except uses AtomicReference from
    atomos.multiprocessing.atomic.
    '''
    def __init__(self, state):
        super(Atom, self).__init__(state)
        self._state = atomic.AtomicReference(state)

    def __repr__(self):
        return util.repr(__name__, self, self._state._proxy_value())
