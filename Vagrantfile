VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # Build Vagrant box based on Fedora 20
    config.vm.box = "chef/fedora-20"

    config.vm.provision "shell", inline: "yum update -y"
end
