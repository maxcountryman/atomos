# -*- coding: utf-8 -*-
'''
Atomos
------

Atomic primitives for Python.

Links
`````
* `documentation <https://atomos.readthedocs.org/en/latest/>`_
* `development version <https://github.com/maxcountryman/atomos>`_
'''

import setuptools

about = {}
with open('atomos/__about__.py') as f:
    exec(f.read(), about)

setuptools.setup(name=about['__title__'],
                 version=about['__version__'],
                 author='Max Countryman',
                 author_email=about['__author__'],
                 description='Atomic primitives for Python.',
                 license=about['__license__'],
                 keywords='atom atomic concurrency lock',
                 url='https://github.com/maxcountryman/atomos',
                 packages=['atomos', 'tests'],
                 long_description=__doc__,
                 classifiers=['Development Status :: 5 - Production/Stable',
                              'Intended Audience :: Developers',
                              'Programming Language :: Python',
                              'Topic :: Utilities',
                              'License :: OSI Approved :: BSD License'],
                 zip_safe=False)
