VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # Build Vagrant box based on Fedora 20
    config.vm.box = "chef/debian-7.6"

    config.vm.provision "shell", inline: "apt-get update"
    config.vm.provision "shell", inline: "apt-get install -y python-pip \
                                                             python-smbus \
                                                             git \
                                                             libzmq-dev \
                                                             python-zmq \
                                                             python-dev \
                                                             python-yaml \
                                                             python-numpy"
    config.vm.provision "shell", inline: "pip install -r /vagrant/requirements.txt"
end
