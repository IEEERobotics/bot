import os
from glob import glob
from setuptools import setup, find_packages

# Setup flags and parameters
pkg_name = 'bbb'  # top-level package name

# Cache readme contents for use as long_description
readme = open('README.md').read()

# Call setup()
setup(
  name=pkg_name,
  version='0.1',
  description='Python BBB I/O library',
  long_description=readme,
  url='https://github.com/jschornick/pybbb',
  author='Jeff Schornick',
  author_email='jeff@schornick.org',
  packages=find_packages(),
  include_package_data=True,
  scripts = glob("examples/*"),
  zip_safe=True,
  test_suite=(pkg_name + '.tests'),
  platforms='any',
  keywords='bbb beaglebone gpio pwm adc',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ])
