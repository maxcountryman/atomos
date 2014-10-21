# Atomos
**Atomic primitives for Python.**

[![Circle CI](https://circleci.com/gh/maxcountryman/atomos.png?style=badge)](https://circleci.com/gh/maxcountryman/atomos)

Atomos is a library of atomic primitives, inspired by Java's
java.util.concurrent.atomic. It provides atomic types for bools, ints, longs,
and floats as well as a generalized object wrapper. In addition, it introduces
[atoms](http://clojure.org/atoms), a concept Clojure programmers will be
familiar with.

## Motivation
Mutable shared state is hard and guess what, it's ubuiquitous in Python. When
working in a multi-threaded context or whenever an application is racing, locks
can be a useful tool. However they can quickly become unweildy.

To address this, Atomos provides wrappers around primitives and objects which
handle the locking semantics for us. These special primitives allow for writing
cleaner, simpler code without having to orchestrate locks directly.

In particular Atomos introduces atoms, a new data type for managing shared
mutable state. Atoms are a near-direct port of Clojure's eponymous data type.
They work by wrapping a given object in compare-and-set semantics.

## Installation

Atomos is available via PyPI.

```shell
$ pip install atomos
```

## Usage
Say we have some shared state in our application. Maybe we have a chat
server which holds state in memory about connected clients. If our
application is threaded we will need some way of sharing this state between
threads.

We can model this state as an atom. This will ensure that when multiple threads
update and retrieve the state, its value is always consistent. For example:

```python
>>> import atomos.atom as atom
>>> state = atom.Atom({'conns': 0, 'active_clients': set([])})
```

Our `state` is an `Atom`, which means we can update it using its `swap` method.
This method works by taking a function which will take the existing state of
the atom and and any arguments or keyword arguments we provide it. It should
return an updated state.

For instance, as a client connects, we want to update the number of connections
and the active client set. We can write a function which we can then pass to
swap to safely mututate our state:

```python
>>> def new_client(cur_state, client):
...     cur_state['conns'] += 1
...     cur_state['active_clients'].add(client)
...     return cur_state
>>> state.swap(new_client, 'foo')
```

Here we have updated our state and can be sure that any other thread which may
have looked at the state only ever saw the state as it was before we called
`swap` or after. However any race condition which might have existed between
incrementing the connections count and adding the client is eliminated, thanks
to our use of the atom.

### Atomic Primitives
Atomos also provides atomic primitives as wrappers around `int`, `long`,
`float`, and `bool` as well as a general wrapper around any object type. We can
use these primitives to construct a thread-safe counter:

```python
>>> import atomos.atomic
>>> counter = atomos.atomic.AtomicInteger()
>>> counter.get()
0
```

To increment the counter, we can call `counter.add_and_get(1)`. This will
return the new value back to us, `1`.

For more complex object types we can use an `AtomicReference`. For instance, we
can wrap any arbitrary class and protect updates to its value like this:

```python
>>> class MyState(object):
...     def __init__(self, foo, bar):
...         self.foo = foo
...         self.bar = bar
>>> state = atomos.atomic.AtomicReference(MyState(42, False))
```

So long as we interact with the `MyState` instance via the `state` wrapper, our
updates will always be protected.

## Multiprocessing
Please note that at this time these data structures will not play nice with
multiprocessing. This is due to the fact that state-sharing between processes
generally requires pickle-able objects.

## Contribution
Contributions are welcome, please ensure PEP8 is followed and that new code is
well-tested prior to making a pull request.
