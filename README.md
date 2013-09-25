# Bot

Code for the IEEE Robotics Team's 2014 robot(s).

## Getting Started

* Satisfy all required [dependencies](README.md#dependencies).
* Use git to [clone our code](README.md#get-the-code).
* [Run our automated unit tests](README.md#testing) to confirm that everything's working.
* Read *and follow* our [style requirements](README.md#style).
* Check GitHub's [issue tracker] to find work we need done and/or report on your progress.

## Style

### Code Style

__It's very important that you follow these requirements *while writing code*, as compared to committing bad code and than (maybe) fixing it later.__

If you don't think you can manage that, please, please set up [pre-commit hooks] to force you to follow good practices.

#### Python

1. Read [PEP8]
2. Re-read [PEP8]
3. Pedantically follow [PEP8]

I suggest running the program pep8 against your code before each commit. You can use the [bot/scripts/check_pep8.sh](scripts/check_pep8.sh) script to test all *.py files in the repo. See the [dependencies](README.md#pep8-checker) section for install instructions.

#### C

[PEP7] will be the standard, but pay special attention to exception #2, as I expect C code will be more likely to pull code blocks from other libs.

Exception 2: "Be consistent with surrounding code...although this is also an opportunity to clean up someone else's mess."

#### Shell

If you really care, give [Google's Shell Style Guide][1] a read. Don't be too pedantic about shell scripts.

### Docstring Style

For general docstring style guidance, see [PEP257]. Specialize your docstrings for Sphinx, as described [here][2]. You may also find [this][3] docstring and Sphinx information helpful.

## Testing

Create unit tests for any code you write. Be sure to run all tests before committing, to validate that you haven't broken anything. I suggest doing this automatically with [pre-commit hooks].

While in the root directory of the project, run our automated tests with:

```bash
python -m unittest discover
```

To run a specific test case, use this syntax (from the root of the repo):

```bash
python -m unittest hardware.tests.test_motor.TestSpeed.test_accel
```

Where `hardware.tests.test_motor.TestSpeed.test_accel` is of the form package.package.module.class.method. Modify that structure to fit your current working directory and/or the path to the test you want to run.

## Hooks, or *How To Make Daniel's Life Easier*

If you're going to be contributing much code, I suggest adding [Git Hooks] to automatically run `python -m unittest discover` and `./scripts/check_pep8.sh` before each commit.

Put this in a new file called `pre-commit`, in the `.git/hooks/` directory (from the project's root). Also, make sure it's executable with `chmod ug+x /path/to/pre-commit`.

```bash
#!/bin/sh

# Run all unit tests
python -m unittest discover
if [ $? -ne 0 ]
then
    echo "Not committing because unit tests failed. Use --no-verify to ignore."
    exit 1
fi

# Check style for conformance with PEP8
./scripts/check_pep8.sh
if [ $? -ne 0 ]
then
    echo "Not committing because check_pep8 failed. Use --no-verify to ignore."
    exit 1
fi
```

## Get the Code

First, make a decision about how you want to structure your file system. Where are you going to store the code? What about robot-related, non-code things? I have a directory `/home/daniel/robot/` that contains subdirectories for each year's work (`2012/`, `2013/`, `current/`). In current, I store the code (`bot/`), along with anything else related to the current year's bot.

Once you know where you're going to store the code, navigate there and then run:

```bash
git clone --recursive git@github.com:NCSUhardware/bot.git
```

If you already have the repo and simply need the [pybbb] submodule (bot/pybbb is empty), then run the following from the root of the repo:

```bash
git pull # Always a good idea
git submodule init
git submodule update
```

The extra submodule-related steps are necessary to retrieve the [pybbb] library (an Open Source project we forked and contributed to) that we use for interaction with the BeagleBone Black. For more information, see the [git-scm section on submodules].

When changes are made to our fork of the [pybbb] library, running `git status` in the root of the repo will show uncommitted changes in `pybbb` (even if you just pulled `bot`, and even if you didn't do anything in `pybbb/`). In short, you just need to navigate to the `pybbb/` directory (`cd pybbb`) and run `git pull`. Backing out to `bot/` and running `git status` should now show no unexpected changes in `pybbb/`.

## Dependencies

### Git

#### Installation

##### Linux (Debian/Ubuntu)

Install with `sudo apt-get install git`. Celebrate. :)

##### Windows / Mac

Download git ([Windows](http://git-scm.com/download/win) / [Mac](http://git-scm.com/download/mac)) and install.

We're not going to use the GUI client, because it doesn't allow you to access the powerful guts of git, its liable to change (making you re-learn everything) and you'll see the same CLI interface on any OS you need to work with in the future.

Search for `git` using your system's built-in search feature. You should find a result for `Git Shell` or `Git Bash`. Open that application and move on to the [configuration section](README.md#configuratoin).

#### Configuration

These instructions are not OS-specific.

Set user-specific info with:

```bash
git config --global user.name "Your Name"
git config --global user.email "youremail@blah.com"
```

If you need more help, see [this guide](https://help.github.com/articles/set-up-git).

To generate and set git to use SSH keys (recommended), follow [this guide](https://help.github.com/articles/generating-ssh-keys).

### Python

We're using Python 2.7.X for this project. If you already have python configured, run `python --version` to check your version.

#### Linux / Mac

You already have Python. Celebrate. :)

#### Windows

Download the Python 2.7.5 installer from [here](http://www.python.org/getit/). Select 32 or 64 bit as appropriate. Install via the typical method.

You'll need to add Python to your path. This is a silly Windows-quirk that I'm not familiar with. TODO: @Arpan, please provide details.

### YAML

If running `which python-yaml` from a shell (likely doesn't work on Windows) returns no results, or if you see `ImportError: No module named yaml` while running code, you're missing YAML.

#### Linux (Debian/Ubuntu)

Run `sudo apt-get install python-yaml`. Celebrate. :)

#### Windows

Try installing via [this](http://pyyaml.org/download/pyyaml/PyYAML-3.10.win32-py2.7.exe) executable (untested).

#### Mac

Open a shell and type `easy_install --version`. If that prints version information, not an error, you have easy_install and this install will be easy.

If you have easy_install, run `sudo easy_install pyyaml`. If that completes without an error, you're good.

If you don't have easy_install, I'm told you can install a Dev Tools package to get it. TODO: @Justin, please confirm.

### ZMQ

#### Linux

Run `sudo apt-get install libzmq-dev python-zmq`. Celebrate. :)

#### Windows / Mac

TODO: How?

### PEP8 Checker

This is a small tool for checking if your code conforms to [PEP8]. I strongly suggest using it, and setting it to run automatically as a [pre-commit hook].

#### Linux

Install with `sudo apt-get install pep8`. Celebrate. :)

#### Windows / Mac

TODO: Has anyone tried this?


[pre-commit hooks]: README.md#hooks-or-how-to-make-daniels-life-easier
[pybbb]: https://github.com/NCSUhardware/pybbb
[git-scm section on submodules]: http://git-scm.com/book/en/Git-Tools-Submodules#Cloning-a-Project-with-Submodules
[PEP8]: http://www.python.org/dev/peps/pep-0008/
[PEP7]: http://www.python.org/dev/peps/pep-0007/
[1]: https://google-styleguide.googlecode.com/svn/trunk/shell.xml
[2]: http://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
[3]: http://stackoverflow.com/questions/5334531/python-documentation-standard-for-docstring
[PEP257]: http://www.python.org/dev/peps/pep-0257/
[multi-OS guide]: https://help.github.com/articles/set-up-git#platform-windows
[Git Hooks]: http://git-scm.com/book/en/Customizing-Git-Git-Hooks
[issue tracker]: https://github.com/NCSUhardware/bot/issues?direction=desc&sort=updated&state=open
