# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # Build Vagrant box based on Fedora 20
    # TODO: Upgrade Vagrant to Debian 8 and install pypy once it's out.
    config.vm.box = "ubuntu/trusty64"

    config.vm.synced_folder ".", "/home/vagrant/bot"

    config.vm.network :private_network, ip: "192.168.33.11"
    config.vm.network "forwarded_port", guest: 80, host: 1234
    config.vm.provision "shell", inline: "apt-get update"
    config.vm.provision "shell", inline: "apt-get install -y python-pip \
                                                             python-smbus \
                                                             git \
                                                             libzmq-dev \
                                                             python-zmq \
                                                             python-dev \
                                                             python-yaml \
                                                             python-numpy \
                                                             "
    config.vm.provision "shell", inline: "pip install -r /home/vagrant/bot/requirements.txt"

        # VM with various useful tools
        # This will take longer to build. It's recommended that folks who
        # already have a reasonable local dev environment use the base
        # VM, edit code locally and then run things in the Vagrant box.
        # The tooled VM is meant for people on shit OSs like Windows who
        # don't have useful tools for development. ;)
        config.vm.provision "shell", inline: "apt-get install -y vim \
                                                                 build-essential \
                                                                 ipython \
                                                                 tmux \
                                                                 screen \
                                                                 nmap \
                                                                 tree \ 
								 python-tox \
								 python-sphinx
								 "


end
