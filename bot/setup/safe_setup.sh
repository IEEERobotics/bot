#!/bin/bash
# Install standard software, do git configuration

# Each should only contain the packages that are added at that level
base="git python-yaml libzmq-dev python-zmq python-simplejson python-smbus python-virtualenv python-pip python-numpy python-dev build-essential vim vim-tiny less cmake pyyaml python-zmq libzbar-dev unzip libopencv-dev python-opencv"

extra="vim-nox ipython tmux screen nmap tree i2c-tools wireless-tools grc"

# Revert setup script after competition

while getopts aubh opt; do
    case $opt in
        a)
            echo "Option: Additional packages"
            install_extra=true
            usb_opts="$usb_opts -a"
            ;;
        u)
            echo "Option: USB install"
            usb_install=true
            ;;
        b)
            echo "Option: Bot specific setup"
            bot_specific=true
            usb_opts="$usb_opts -b"
            ;;
        *)
            echo "Help"
            echo "  -a  Install additional packages: $extra"
            echo "  -u  Initiate install over USB"
            echo "  -b  Perform bot-specific setup (networking, etc)"
            exit 1
            ;;
  esac
done

# Verify we're on an actual BeagleBone
if grep -q AM33XX /proc/cpuinfo; then
    echo "BeagleBone detected!"
else
    echo "This doesn't look like a BeagleBone!"
    echo "Aborting (use -u to connect over USB)"
    exit 1
fi

# TODO: add vimrc, bashrc, tmux.conf
echo "========================"
echo "Populating filesystem..."
echo "========================"
chown -R root.root fs-*
rsync -va fs-common/* /
chmod 755 /root/.ssh
chmod 600 /root/.ssh/id_rsa
chmod 644 /root/.ssh/authorized_keys
# We need to customize uEnv.txt for each install
ROOT_UUID=$(blkid -t LABEL=rootfs -o value -s UUID)
sed 's/{{ROOT_UUID}}/'$ROOT_UUID'/' /boot/uboot/uEnv_template.txt > /boot/uboot/uEnv.txt

if [ "$bot_specific" = true ]; then
    rsync -va fs-bot/* /
    echo "============================"
    echo "Enabling bot wireless uplink"
    echo "============================"
fi

echo "=================="
echo "Testing network..."
echo "=================="
if  /bin/ping -c1 -w1 google.com; then
    echo "Network is live"
else
    echo "No network connection detected, attempting to route via USB..."
    route add default gw 192.168.7.1
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
    if  /bin/ping -c1 -w1 google.com; then
        echo "Network is temporarily live for install"
    else
        echo "Aborting setup due to lack of connectivty!"
        exit 1
    fi
fi
echo

echo "========================="
echo "Updating package listings"
echo "========================="
apt-get update
update-rc.d bbb defaults
cp /usr/share/zoneinfo/America/New_York /etc/localtime

echo "==================="
echo "Installing packages"
echo "==================="
echo "Installing required packages"
apt-get -y install $base
echo
if [ "$install_extra" = true ]; then
    echo "Installing extra packages"
    apt-get -y install $extra
fi

BASE_DIR=$HOME

fetch_git_repo() {
    REPO=$1
    echo "Git repo: $REPO"
    if [ -z "$2" ]; then
        DEST=$(echo $REPO | cut -d/ -f2)
    else
        DEST=$2
    fi
    cd $BASE_DIR
    if [ ! -d $DEST/.git ]; then
        echo "Cloning $REPO into $BASE_DIR/$DEST"
        echo git clone --recursive git@github.com:${REPO}.git $DEST
        git clone --recursive git@github.com:${REPO}.git $DEST
    fi
    cd $BASE_DIR/$DEST
    git pull
    # reset hard?
}

# Configure git and fetch all the repos we use
echo "========================="
echo "Fetching git repositories"
echo "========================="
echo "Configuring git..."
git config --global user.name "ncsubot"
git config --global user.email "ncsubot@gmail.com"
fetch_git_repo IEEERobotics/bot
fetch_git_repo NCSUhardware/DMCC_Library
fetch_git_repo jschornick/i2c_device
fetch_git_repo jschornick/pypruss
fetch_git_repo beagleboard/am335x_pru_package

echo "======================================"
echo "Building and installing PRU library..."
echo "======================================"

python_module() {
    MODULE=$1
    echo "-------------------------------"
    echo "Python module: $MODULE"
    echo "-------------------------------"
    cd $BASE_DIR/$MODULE
    python setup.py install
}

python_module i2c_device
python_module DMCC_Library
python_module pypruss
python_module sympy
python_module Pillow

# Zbar doesn't work when installed from pip/apt-get, no idea why
echo "Install zbar"
wget https://github.com/npinchot/zbar/archive/master.zip
unzip master.zip 
cd zbar-master
python setup.py install


echo "==============="
echo "Cleaining up..."
echo "==============="
cd $BASE_DIR
rm -rf fs-bot fs-common setup_bone.sh

echo "Done with local install"
