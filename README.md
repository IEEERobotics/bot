[![Build Status](https://travis-ci.org/IEEERobotics/bot.svg?branch=master)](https://travis-ci.org/IEEERobotics/bot)

For meetings, news, and google hangouts, [check out our calender](https://www.google.com/calendar/embed?src=bmNzdS5lZHVfazY1dm5lZTBjcHQ5cmhvbTlzOGQ4dGlna3NAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ), and join our [email list](https://groups.google.com/a/ncsu.edu/forum/?hl=en#!forum/group-ieee-robotics-announce).

# Bot

Code for the NCSU IEEE Robotics Team's robot(s).

- [Bot](#user-content-bot2014)
    - [Overview](#user-content-overview)
    - [Code Style](#user-content-code-style)
    - [Docstring Style](#user-content-docstring-style)
    - [Testing](#user-content-testing)
    - [Docker](#user-content-docker)
    - [Vagrant](#user-content-vagrant)
    - [Dependencies](#user-content-dependencies)
        - [Dependencies: Git](#user-content-dependencies-git)
        - [Dependencies: Vagrant](#user-content-dependencies-vagrant)
          - [Kernel Errors](#user-content-kernel-errors)
        - [Dependencies: Docker](#user-content-dependencies-docker)

## Overview

This is the main codebase for the IEEE Robotics Team. Don't be intimidated! We've recently done some cool work to make your life as a dev much, much easier. You can use [Vagrant] and/or [Docker] to trivially stand up a standardized, batteries-included dev environment. You can also be confident your changes haven't broken anything by running our Tox-driven unittests while developing. Once you push your code, all tests will automatically be run in our [Travis] Continuous Integration environment, which will handle emailing folks when things break and updating the build status badge at the top of this README. Unfamiliar with the codebase? No worries, it's incredibly well documented! Look for docstrings at the top of every module, class and method. Looking for some non-code docs? Check out our GitHub-hosted [wiki]! Need a task to work on, or need to report a bug, request a feature or ask a question? Head over to our GitHub [Issue] tracker!

All we ask in return is that you do your best to keep the codebase healthy by writing unittests, documenting your code with docstrings and in-line comments, following [PEP8] style conventions, and being a good community member by keeping the [wiki] up-to-date, the [Issue] tracker clean and our build status badge green. Happy hacking!

## Code Style

1. Read [PEP8]
2. Re-read [PEP8]
3. Pedantically follow [PEP8]

To check for PEP8 conformance, run `tox -epep8`. See the Testing section for details.

## Docstring Style

For general docstring style guidance, see [PEP257]. Specialize your docstrings for Sphinx, as described [here][2]. You may also find [this][3] docstring and Sphinx information helpful. Looking at existing well-done docstrings is a solid approach.

## Testing

The project uses Tox to run unit tests, confirm that Sphinx-gen'd docs build and verify that the code conforms to [PEP8] style. To kick off all tests, simply issue the `tox` command in the project's root. Note that Tox automatically builds and brings down virtual environments, installing required dependences as it does.

```
root@5d8d6d5e188f:/opt/bot# tox
<snip>
  py27: commands succeeded
  docs: commands succeeded
  pep8: commands succeeded
  congratulations :)
```

To run a specific set of tests in a virtual environment, use `tox -e<name of tests>`. For example, `tox -epep8` to run [PEP8] style checks or `tox -epy27` to run unit tests with a Python 2.7 interpreter.

Our codebase is pretty awesome in that it supports standing up both [Vagrant] and [Docker] environments. The environments created there are pre-configured to completely support our code, so you don't have to do that work on your dev system. When testing, you should use one of those well-understood, documented, reproducible environments. See the [Vagrant](#user-content-vagrant) and [Docker](#user-content-docker) sections for details.

Another awesome thing about our codebase is that it's configured to do Continuous Integration using [Travis] CI. Every time a change is made to the code, an automated [Travis] job kicks off and runs all of our tests (unit tests, [PEP8] style tests, builds the docs). If the build breaks, the badge at the top of this README turns red and the people listed in our `.travis.yml` file get notified via email. Keeping our project's badge green is a matter of pride. Don't fail us. ;)

## Docker

[Docker] makes use of containers that work at a process level, compared to [Vagrant]'s OS level isolation. This makes [Docker] images much more fast and lightweight. However, [Docker] support for Windows is in its very early stages and not yet ready for consumption, which is one plus for [Vagrant]. Linux users should prefer [Docker].

Aside: [Docker] is one of the sexiest new technologies around. If you get proficient with it, you should put that on your CV.

If you haven't already, head over to the [Dependencies: Docker](#user-content-dependencies-docker) section and get [Docker] setup on your dev box.

We have an [Automated Build configured on DockerHub](https://registry.hub.docker.com/u/ieeerobotics/bot/). For every change of the codebase, our `Dockerfile` is executed to create an up-to-date [Docker] image automatically by DockerHub. To grab a totally configured environment with the latest code, simply run:

```
[~/bot2014]$ docker pull ieeerobotics/bot
```

The default process that will be executed in our [Docker] image is given by the `CMD ["./start.py", "-Tsc"]` line in our `Dockerfile`. So, unless you override that default, `docker run` commands will start a client and server in test mode (simulating fake hardware).

TODO: There's currently an issue with this. Simulated pin files must be created by running tests first. Working on it.

```
[~/bot2014]$ docker run -ti ieeerobotics/bot
<snip>
```

You can run tests like this:

```
[~/bot2014]$ docker run -ti ieeerobotics/bot bash
<snip>
root@5d8d6d5e188f:/opt/bot/bot# cd ..
root@5d8d6d5e188f:/opt/bot# tox
<snip>
```

TODO: Description of code+test work flow

## Vagrant

[Vagrant] allows you to trivially spin up a VM that's totally configured to support our codebase. It isolates its environment at an OS level, instead of a process level like [Docker]. This makes it slower. However, [Vagrant] is supported on Windows where [Docker] is not.

Note: If you don't have [Vagrant] installed/configured, head over to the [Dependencies: Vagrant](#user-content-dependencies-vagrant) section.

Now that the work of creating a `Vagrantfile` is done, you can spin up a [Vagrant] environment with a simple one-liner:

```
# General form: vagrant up <name of box>
[~/bot2014]$ vagrant up base
```

If this is your first time using the [Vagrant] image we build on, it'll be downloaded from VagrantCloud for you. That may take some time, but it'll be cached locally for future use.

There are actually two [Vagrant] boxes defined in our `Vagrantfile`. One, called `base`, provides only the minimum required to run the codebase. The other, called `tooled`, adds various useful dev tools to the `base` box. The `tooled` box is meant for folks that don't have good development environments set up locally (ie, Windows). For folks with dev environments they are comfortable with already, use the `base` box, edit code on your host and then run tests and/or the CLI/Server in [Vagrant]. Everything in the root of the repo is synced with `/home/vagrant/bot` in both [Vagrant] boxes.

Once a box is built and up, you can connect to it with this equally trivial command:

```
# General form: vagrant ssh <name of box> 
[~/bot2014]$ vagrant ssh base
```

You'll be given a shell in the [Vagrant] VM. Navigate around and run tests as normal.

```
vagrant@packer-debian-7:~$ ls
bot  src
vagrant@packer-debian-7:~$ cd bot/
vagrant@packer-debian-7:~/bot$ ls
bot  Dockerfile  docs  LICENSE.txt  README.md  requirements.txt  setup.py  tests  tox.ini  Vagrantfile
vagrant@packer-debian-7:~/bot$ tox
<snip test output>
```

## Dependencies

Now that we have super-sexy [Vagrant] and [Docker] environments, our dependencies are almost completely handled for you. All you'll need to do is to your machine is install git for working with the code, [Vagrant] for standing up [Vagrant] environments and [Docker] for standing up [Docker] environments.

### Dependencies: Git

We version control our code with git, because welcome to the 2000s. Head over to our [wiki page on Git](https://github.com/IEEERobotics/bot2014/wiki/Git) for instructions about how to install and configure it if you're not a git-ninja already.

### Dependencies: Vagrant

Head over to the [Vagrant Downloads](https://www.vagrantup.com/downloads.html) page and grab the latest version of [Vagrant] for your OS. Fedora/RHEL/CentOS folks need the RPM package, Ubuntu/Debian folks need the DEB package. Note that [Vagrant] also supports Windows and OSX.

Assuming you're on Fedora/RHEL/CentOS, find the .rpm file you just downloaded and install it:

```
sudo rpm -i <name of rpm>
```

[Vagrant] uses various "providers" for virtualization support. By default, it uses VirtualBox. If you don't have VirtualBox installed, you'll see an error message when you try to `vagrant up` anything. Install VirtualBox (Fedora/RHEL/CentOS):

```
sudo yum install VirtualBox -y
```

#### Kernel Errors

If you get a kernel upgrade in a normal `sudo yum update`, you may need to re-update your VirtualBox kernel modules.

```
sudo yum install kmod-VirtualBox -y
sudo systemctl restart systemd-modules-load.service
```

### Dependencies: Docker

[Docker] supports most major OSs, including very recent support for Windows. The following instructions are for Fedora. More info about installation on other OSs [here](https://docs.docker.com/installation/).

Install the `docker-io` (not `docker`!) package:

```
sudo yum install docker-io -y
```

Start the [Docker] daemon and configure it to start at boot:

```
sudo systemctl start docker
sudo systemctl enable docker
```

To avoid having to run all [Docker] commands as root, add your user to the `docker` group:

```
sudo usermod -a -G docker <your username here>
```

You may need to reboot for the `usermod` step take effect.

To verify that everything worked, grab [an image from DockerHub](https://registry.hub.docker.com/_/debian/) and make sure you can run commands:

```
# Will need to prepend "sudo" if you haven't rebooted after usermod step
docker run -ti debian:7 echo "Hello world!"
```

[Vagrant]: https://docs.vagrantup.com/v2/A
[Docker]: https://docs.docker.com/
[Travis]: https://travis-ci.org/IEEERobotics/bot2014
[wiki]: https://github.com/IEEERobotics/bot2014/wiki
[Issue]: https://github.com/IEEERobotics/bot2014/issues
[PEP8]: http://www.python.org/dev/peps/pep-0008/
[2]: http://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example
[3]: http://stackoverflow.com/questions/5334531/python-documentation-standard-for-docstring
[PEP257]: http://www.python.org/dev/peps/pep-0257/
