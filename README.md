[![Build Status](https://travis-ci.org/IEEERobotics/bot2014.svg?branch=master)](https://travis-ci.org/IEEERobotics/bot2014)

# Bot2014

Code for the NCSU IEEE Robotics Team's robot(s).

## Overview

This is the main codebase for the IEEE Robotics Team. Don't be intimidated! We've recently done some cool work to make your life as a dev much, much easier. You can use [Vagrant] and/or [Docker] to trivially stand up a standardized, batteries-included dev environment. You can also be confident your changes haven't broken anything by running our Tox-driven unittests while developing. Once you push your code, all tests will automatically be run in our [Travis] Continuous Integration environment, which will handle emailing folks when things break and updating the _build status_ badge at the top of this README. Unfamiliar with the codebase? No worries, it's incredibly well documented! Look for docstrings at the top of every module, class and method. Looking for some non-code docs? Check out our GitHub-hosted [wiki]! Need a task to work on, or need to report a bug, request a feature or ask a question? Head over to our GitHub [Issue] tracker!

All we ask in return is that you do your best to keep the codebase healthy by writing unittests, documenting your code with docstrings and in-line comments, following [PEP8] style conventions, and being a good community member by keeping the [wiki] up-to-date, the [Issue] tracker clean and our _build status_ badge green. Happy hacking!

## Code Style

1. Read [PEP8]
2. Re-read [PEP8]
3. Pedantically follow [PEP8]

## Docstring Style

For general docstring style guidance, see [PEP257]. Specialize your docstrings for Sphinx, as described [here][2]. You may also find [this][3] docstring and Sphinx information helpful. Looking at existing well-done docstrings is a solid approach.

## Testing

The project uses Tox to run unit tests with various Python interpreters, confirm that Sphinx-gen'd docs build and test that the code conforms to [PEP8] style. To kick off all tests, simply issue the `tox` command in the project's root. Note that Tox automatically builds and brings down virtual environments, installing required dependences as it does.

```
[~/perf]$ tox
<snip>
  py27: commands succeeded
  docs: commands succeeded
  pep8: commands succeeded
  congratulations :)
```

To run a specific set of tests in a virtual environment, use `tox -e<name of tests>`. For example, `tox -epep8` to run [PEP8] style checks or `tox -epy27` to run unit tests with a Python 2.7 interpreter.

## Dependencies

### Git

We version control our code with git, because welcome to the 2000s. Head over to our [wiki page on Git](https://github.com/IEEERobotics/bot2014/wiki/Git) for instructions about how to install and configure it if you're not a git-ninja already.

### Vagrant

TODO

### Docker

TODO

[Vagrant]: https://docs.vagrantup.com/v2/A
[Docker]: https://docs.docker.com/
[Travis]: https://travis-ci.org/IEEERobotics/bot2014
[wiki]: https://github.com/IEEERobotics/bot2014/wiki
[Issue]: https://github.com/IEEERobotics/bot2014/issues
[PEP8]: http://www.python.org/dev/peps/pep-0008/
[2]: http://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
[3]: http://stackoverflow.com/questions/5334531/python-documentation-standard-for-docstring
[PEP257]: http://www.python.org/dev/peps/pep-0257/
