# Dirty hack to make tests work in Vagrant env
# Remove once this is fixed: http://bugs.python.org/issue8876
import os
del os.link

from setuptools import setup, find_packages

setup(
    name="bot",
    version="1.0.1",
    description="NCSU IEEE Robotics Team Codebase",
    url="https://github.com/IEEERobotics/bot2014/",
    author="NCSU IEEE Robotics",
    author_email="dfarrell07@gmail.com",
    # See for more classifer options: http://goo.gl/8jtDH4
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: BSD License",
    ],
    keywords="NCSU IEEE Robotics robot bot hardware",
    packages=find_packages(),
    # TODO: Fix for this style test layout
    test_suite="tests",
    # See for more install_requires info: http://goo.gl/vCOKSw
    # See for more install_requires info: http://goo.gl/5zQKIF
    # TODO: List all known minimum requirements
    install_requires=["pyyaml"],
    # TODO: List dev and test env requirements
    extras_require={
        "dev": [],
        "test": ["tox", "flake8"],
    },
    # TODO: Do we need to specify any package data?
    # ^^See: https://github.com/pypa/sampleproject/blob/master/setup.py#L81
    # TODO: Do we need to define an entry point?
    # ^^See: https://github.com/pypa/sampleproject/blob/master/setup.py#L95
)
