:orphan:

======
Atomos
======

.. module:: atomos

Atomic primitives for Python.

Atomos is a library of atomic primitives, inspired by Java's java.util.concurrent.atomic. It provides atomic types for bools, ints, longs, and floats as well as a generalized object wrapper. In addition, it introduces `atoms`_, a concept Clojure programmers will be familiar with.

.. _atoms: http://clojure.org/atoms

Installation
============

Atomos is available via PyPI. ::

    $ pip install atomos

Usage
=====

A short tutorial is presented in the `README`_.

.. _README: https://github.com/maxcountryman/atomos#usage

API
===
.. autoclass:: atomos.atom.Atom
    :members:

.. autoclass:: atomos.atom.ARef
    :members:

.. autoclass:: atomos.atomic.AtomicReference
    :members:

.. autoclass:: atomos.atomic.AtomicBoolean
    :members:

.. autoclass:: atomos.atomic.AtomicInteger
    :members:

.. autoclass:: atomos.atomic.AtomicLong
    :members:

.. autoclass:: atomos.atomic.AtomicFloat
    :members:
