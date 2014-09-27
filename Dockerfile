# Base the image on Debian 7
# Picked Debian because it's small and what runs on the bot
# https://registry.hub.docker.com/_/debian/
FROM debian:7
MAINTAINER Daniel Farrell <dfarrell07@gmail.com>

# These are the packages installed via setup/setup_bone.sh
# https://github.com/IEEERobotics/bot2014/blob/master/setup/setup_bone.sh
# TODO: Am I buiding a dev env or just something that can run the software?
RUN apt-get update && apt-get install -y git \
                                         python \
                                         python-yaml \
                                         python-simplejson \
                                         libzmq-dev \
                                         python-zmq \
                                         python-numpy \
                                         python-smbus \
                                         python-virtualenv \
                                         tmux \
                                         rsync \
                                         python-pip \
                                         python-dev \
                                         build-essential \
                                         vim \
                                         vim-tiny \
                                         less \
                                         cmake \
                                         ipython \
                                         nmap \
                                         tree \
                                         vim-nox \
                                         screen \
                                         i2c-tools \
                                         wireless-tools \
                                         grc
