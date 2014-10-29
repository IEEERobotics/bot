VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # Build Vagrant box based on Fedora 20
    # TODO: Upgrade Vagrant to Debian 8 and install pypy once it's out.
    config.vm.box = "chef/debian-7.6"

    config.vm.provision "shell", inline: "apt-get update"
    config.vm.provision "shell", inline: "apt-get install -y python-pip \
                                                             python-smbus \
                                                             git \
                                                             libzmq-dev \
                                                             python-zmq \
                                                             python-dev \
                                                             python-yaml \
                                                             python-numpy \
                                                             python3.2"
    config.vm.provision "shell", inline: "pip install -r /vagrant/requirements.txt"
end
