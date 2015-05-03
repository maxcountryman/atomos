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

import sys

import setuptools
from setuptools.command.test import test as TestCommand


about = {}
with open('atomos/__about__.py') as f:
    exec(f.read(), about)

setup_requires = ['pytest', 'tox']
install_requires = ['six', 'tox']
tests_require = ['pytest-cov', 'pytest-cache', 'pytest-timeout']


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long',
                          '--cov', 'atomos', '--cov-report',
                          'term-missing', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

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
                 cmdclass={'test': PyTest},
                 setup_requires=setup_requires,
                 install_requires=install_requires,
                 tests_require=tests_require,
                 zip_safe=False)
