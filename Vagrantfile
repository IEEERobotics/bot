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
    config.vm.synced_folder ".", "/home/vagrant/bot"

    config.vm.define "base" do |base|
        # Just the shared config above
    end

    config.vm.define "tooled" do |tooled|
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
                                                                 tree"
    end

end
