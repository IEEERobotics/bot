# Bot

Code for the IEEE Robotics Team's 2014 robot(s).

## Getting Started

If you're pulling the code for the first time, navigate to the directory where you'd like to store the repo and then run:

```bash
git clone --recursive git@github.com:NCSUhardware/bot.git
```

If you already have the repo and simply need the [pybbb] submodule (bot/pybbb is empty), then run the following from the root of the repo:

```bash
git pull # Always a good idea
git submodule init
git submodule update
```

The extra submodule-related steps are necessary to retrieve the [pybbb] library that we use for interaction with the BeagleBone Black. For more information, see the [git-scm section on submodules].

You likey don't have python-yaml installed by default. It's required for reading YAML files, which therefore makes it a hard requirement for running most of our code.

If runing `which python-yaml` from a shell returns no results, you'll need to install the python-yaml package with your perfered package manager (ie `apt-get install python-yaml`).

## Style

### Code Style

#### Python

1. Read [PEP8]
2. Re-read [PEP8]
3. Pedantically follow [PEP8]

I suggest running the program pep8 against your code before each commit. You can use the bot/scripts/check_pep8.sh script to test all *.py files in the repo. The pep8 package is likely available by default in your Linux distro's repos (tested on Ubuntu), but you'll need to install it (ie `sudo apt-get install pep8`, `yum install pep8`, `pip install pep8`, `easy_install pep8`).

#### C

[PEP7] will be the standard, but pay special attention to exception #2, as I expect C code will be more likely to pull code blocks from other libs.

Exception 2: "Be consistent with surrounding code...although this is also an opportunity to clean up someone else's mess."

#### Shell

If you really care, give [Google's Shell Style Guide][1] a read. Don't be too pedantic about shell scripts.

### Docstring Style

For general docstring style guidence, see [PEP257]. Specialize your docstrings for Sphinx, as described [here][2]. You may also find [this][3] docstring and Sphinx information helpful.

## Testing

Create unit tests for any code you write. Be sure to run all tests before committing, to validate that you haven't broken anything.

While in the root directory of the project, run our automated tests with:

```bash
python -m unittest discover
```

To run a specific test case, use this syntax (from the root of the repo):

```bash
python -m unittest hardware.tests.test_motor.TestSpeed.test_accel
```

Where `hardware.tests.test_motor.TestSpeed.test_accel` is of the form package.package.module.class.method. Modify that structure to fit your current working directory and/or the path to the test you want to run.

[pybbb]: https://github.com/NCSUhardware/pybbb
[git-scm section on submodules]: http://git-scm.com/book/en/Git-Tools-Submodules#Cloning-a-Project-with-Submodules
[PEP8]: http://www.python.org/dev/peps/pep-0008/
[PEP7]: http://www.python.org/dev/peps/pep-0007/
[1]: https://google-styleguide.googlecode.com/svn/trunk/shell.xml
[2]: http://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
[3]: http://stackoverflow.com/questions/5334531/python-documentation-standard-for-docstring
[PEP257]: http://www.python.org/dev/peps/pep-0257/
