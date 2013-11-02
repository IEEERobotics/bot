#!/usr/bin/env bash
# Install standard software, do git configuration

sudo apt-get install ipython \
                     vim \
                     tmux \
                     pep8 \
                     git \
                     python-yaml \
                     libzmq-dev \
                     python-zmq \
                     python-numpy \
                     nmap \
                     tree \
                     screen \
                     build-essential \
                     python-pip \
                     python-dev \
                     python-smbus \
                     python-yaml \
                     i2c-tools \
                     wireless-tools \

git config --global user.name "ncsubot"
git config --global user.email "ncsubot@gmail.com"
