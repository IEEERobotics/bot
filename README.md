# Bot2014

Code for the IEEE Robotics Team's 2014 robot(s).

## Getting Started

* Satisfy all required [dependencies](README.md#dependencies).
* Use git to [clone our code](README.md#get-the-code).
* [Run our automated unit tests](README.md#testing) to confirm that everything's working.
* Read *and follow* our [style requirements](README.md#style).
* Check GitHub's [issue tracker] to find work we need done and/or report on your progress.

## GitHub: Issues and Wiki

We use GitHub's [issues](https://github.com/IEEERobotics/bot2014/issues) feature to report and track bugs, tasks, feature requests, questions and generally any thread that's related to the code. Checking the issues frequently keeps you up to date on the work being done, the work that needs to be done (please contribute!) and anything that may be wrong with code you're responsible for.

As the code matures, we'll put more effort into developing this repo's [wiki](https://github.com/IEEERobotics/bot2014/wiki). As you find things that should be documented, please feel free to edit wiki pages and create your own. 

## Style

### Code Style

__It's very important that you follow these requirements *while writing code*, as compared to committing bad code and than (maybe) fixing it later.__

If you don't think you can manage that, please, please set up [pre-commit hooks] to force you to follow good practices.

#### Python

1. Read [PEP8]
2. Re-read [PEP8]
3. Pedantically follow [PEP8]

I suggest running the program pep8 against your code before each commit. You can use the [bot2014/scripts/check_pep8.sh](scripts/check_pep8.sh) script to test all *.py files in the repo. See the [dependencies](README.md#pep8-checker) section for install instructions.

### Docstring Style

For general docstring style guidance, see [PEP257]. Specialize your docstrings for Sphinx, as described [here][2]. You may also find [this][3] docstring and Sphinx information helpful.

## Testing

Create unit tests for any code you write. Be sure to run all tests before committing, to validate that you haven't broken anything. I suggest doing this automatically with [pre-commit hooks].

While in the root directory of the project, run our automated tests with:

```bash
./start.py -t
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
git clone --recursive git@github.com:IEEERobotics/bot2014.git
```

If you already have the repo and simply need the [pybbb] submodule (`bot2014/pybbb` is empty), then run the following from the root of the repo:

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

##### Mac

Download [git](http://git-scm.com/download/mac) and install.

We're not going to use the GUI client, because it doesn't allow you to access the powerful guts of git, it's liable to change (making you re-learn everything) and you'll see the same CLI interface on any OS you need to work with in the future.

Search for "git" using your system's built-in search feature. You should find a result for `Git Shell` or `Git Bash`. Open that application and move on to the [configuration section](README.md#configuratoin).

#### Configuration

These instructions are not OS-specific.

Set user-specific info with:

```bash
git config --global user.name "Your Name"
git config --global user.email "youremail@blah.com"
```

If you need more help, see [this guide](https://help.github.com/articles/set-up-git).

To generate and set git to use SSH keys (recommended), follow [this guide](https://help.github.com/articles/generating-ssh-keys).

Once you get everything set up, I suggest going though [this quick, interactive tutorial](http://try.github.io/levels/1/challenges/1).

### Python

We're using Python 2.7.x for this project. If you already have python configured, run `python --version` to check your version.

#### Linux (Debian/Ubuntu) / Mac

You already have Python. Celebrate. :)

### YAML

If running `which python-yaml` from a shell returns no results, or if you see `ImportError: No module named yaml` while running code, you're missing YAML.

#### Linux (Debian/Ubuntu)

Run `sudo apt-get install python-yaml`. Celebrate. :)

#### Mac

Open a shell and type `easy_install --version`. If that prints version information, not an error, you have easy_install and this install will be easy.

If you have easy_install, run `sudo easy_install pyyaml`. If that completes without an error, you're good.

If you don't have easy_install, I'm told you can install a Dev Tools package to get it. TODO: @Justin, please confirm.

### ZMQ

#### Linux (Debian/Ubuntu)

Run `sudo apt-get install libzmq-dev python-zmq`. Celebrate. :)

#### Mac

Run `sudo pip install pyzmq`. If pip is not found, run `sudo easy_install pip` first, and try again.

Note that a direct `sudo easy_install pyzmq` might also work, however [pip is preferable for several reasons](http://stackoverflow.com/questions/3220404/why-use-pip-over-easy-install), including the fact that it allows you to uninstall packages (for real!).

### PEP8 Checker

This is a small tool for checking if your code conforms to [PEP8]. I strongly suggest using it, and setting it to run automatically as a [pre-commit hook].

#### Linux (Debian/Ubuntu)

Install with `sudo apt-get install pep8`. Celebrate. :)

#### Mac

Same deal as pyzmq: `sudo pip install pep8`

Verify installation by running `pep8` on your terminal. If it is not found even after a successful installation, it may be that pep8 has been installed correctly as a python package, but the script is not available on your path. One recommended solution is to soft-link the `pep8` executable script to a location on your path.

For instance, on a Mac OS X 10.8, pip installed pep8 at `/Library/Frameworks/Python.framework/Versions/2.7/bin/pep8` and `/usr/local/bin/` is a location on my path, so a soft link can be created using the command:

`ln -s /Library/Frameworks/Python.framework/Versions/2.7/bin/pep8 /usr/local/bin/`

Adapt according to paths on your system. Again, verify by running `pep8` from the terminal.

### NumPy

#### Linux (Debian/Ubuntu)

Install with `sudo apt-get install python-numpy`. Celebrate. :)

#### Mac

TODO: How?


[pre-commit hooks]: README.md#hooks-or-how-to-make-daniels-life-easier
[pre-commit hook]: README.md#hooks-or-how-to-make-daniels-life-easier
[pybbb]: https://github.com/IEEERobotics/pybbb
[git-scm section on submodules]: http://git-scm.com/book/en/Git-Tools-Submodules#Cloning-a-Project-with-Submodules
[PEP8]: http://www.python.org/dev/peps/pep-0008/
[PEP7]: http://www.python.org/dev/peps/pep-0007/
[1]: https://google-styleguide.googlecode.com/svn/trunk/shell.xml
[2]: http://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
[3]: http://stackoverflow.com/questions/5334531/python-documentation-standard-for-docstring
[PEP257]: http://www.python.org/dev/peps/pep-0257/
[multi-OS guide]: https://help.github.com/articles/set-up-git#platform-windows
[Git Hooks]: http://git-scm.com/book/en/Customizing-Git-Git-Hooks
[issue tracker]: https://github.com/IEEERobotics/bot2014/issues?direction=desc&sort=updated&state=open
