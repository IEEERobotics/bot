import os
from glob import glob
from setuptools import setup, find_packages
import unittest

# Setup flags and parameters
pkg_name = 'bot2014'  # top-level package name

# Cache readme contents for use as long_description
readme = open('README.md').read()

# Call setup()
setup(
  name=pkg_name,
  version='0.1',
  description='NCSU IEEE Bot 2014',
  long_description="NCSU IEEE Bot 2014",
  author='NCSU IEEE',
  author_email='group-ieee-robotics@ncsu.edu',
  packages=find_packages(),
  include_package_data=True,
  scripts = glob("start.py"),
  zip_safe=True,
  install_requires=[
    'pyDMCC'
  ],
  test_suite='tests',
  platforms='any',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2.7',
  ])
