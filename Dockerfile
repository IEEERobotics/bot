# Base the image on Debian 7
# Picked Debian because it's small and what runs on the bot
# https://registry.hub.docker.com/_/debian/
FROM debian:7
MAINTAINER Daniel Farrell <dfarrell07@gmail.com>

# These are the packages installed via setup/setup_bone.sh
# https://github.com/IEEERobotics/bot2014/blob/master/setup/setup_bone.sh
RUN apt-get update && apt-get install -y git \
                                         python \
                                         python-dev \
                                         python-yaml \
                                         python-simplejson \
                                         libzmq-dev \
                                         python-zmq \
                                         python-numpy \
                                         python-smbus \
                                         python-pip \
                                         pep8

# Clone required repos into /src
RUN git clone https://github.com/IEEERobotics/DMCC_Library.git /src/DMCC_Library
RUN git clone https://github.com/jschornick/i2c_device.git /src/i2c_device

# Install required repos
RUN cd /src/i2c_device && python setup.py install
RUN cd /src/DMCC_Library && python setup.py install

# Drop source (bot2014, current context) in /src dir
# Do the ADD as late as possible, as it invalidates cache
ADD . /src/bot2014

WORKDIR /src/bot2014
CMD ["./start.py", "-Ts"]
