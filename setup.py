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

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


about = {}
with open('atomos/__about__.py') as f:
    exec(f.read(), about)

setup_requires = ['pytest', 'tox']
install_requires = ['six', 'tox']
tests_require = ['pytest-cov', 'pytest-cache', 'pytest-timeout']
dev_requires = ['pyflakes', 'pep8', 'pylint', 'check-manifest',
                'ipython', 'ipdb', 'sphinx']
dev_requires.append(tests_require)


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

setup(name=about['__title__'],
      version=about['__version__'],
      author='Max Countryman',
      author_email=about['__author__'],
      description='Atomic primitives for Python.',
      license=about['__license__'],
      keywords='atom atomic concurrency lock',
      url='https://github.com/maxcountryman/atomos',
      packages=find_packages(exclude=['docs', 'tests']),
      long_description=__doc__,
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Utilities',
                   'License :: OSI Approved :: BSD License'],
      cmdclass={'test': PyTest},
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={
          'dev': dev_requires,
          'test': tests_require,
      },
      zip_safe=False)
