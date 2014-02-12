#!/usr/bin/env bash
# Install standard software, do git configuration

EX_USAGE=64
BASE=$HOME

# Each should only contain the packages that are added at that level
light="git python-yaml libzmq-dev python-zmq python-simplejson"
medium="ipython vim python-numpy"
full="tmux screen nmap tree build-essential python-pip python-dev python-smbus i2c-tools wireless-tools"

echo "[l]ight will install packages necessary for basic functionally:"
echo $light
echo "[m]edium will add numpy (large) and a few very-helpful tools:"
echo $medium
echo "[f]ull will install everything:"
echo $full
echo "Note: Full implies medium and light, medium implies light."
echo "      Doing one then later doing another is fine."
echo -n "[l]ight, [m]edium or [f]ull setup? [l/M/f] "
read type

sudo apt-get update
if [ "$type" == "l" -o "$type" == "L" ]
then
    sudo apt-get install $light
elif [ "$type" == "m" -o "$type" == "M" -o $type == "" ]
then
    sudo apt-get install $light $medium
elif [ "$type" == "f" -o "$type" == "F" ]
then
    sudo apt-get install $light $medium $full
else
    echo "Invalid response." >&2
    exit $EX_USAGE
fi

export EDITOR=vim

# Configure git
echo "Configuring git..."
git config --global user.name "ncsubot"
git config --global user.email "ncsubot@gmail.com"

# Add SSH keys
if [ ! -f ~/.ssh/id_rsa ]
then
    echo "SSH keys don't exist."
    echo "Add SSH keys? [Y/n] "
    read add_keys

    if [ "$add_keys" == "y" -o "$add_keys" == "Y" -o "$add_keys" == "" ]
    then
        echo "Adding SSH keys..."
        mkdir -p ~/.ssh/
        wget --no-check-certificate -O ~/.ssh/id_rsa https://raw.github.com/NCSUhardware/bot/master/os/fs/root/.ssh/id_rsa?token=2446394__eyJzY29wZSI6IlJhd0Jsb2I6TkNTVWhhcmR3YXJlL2JvdC9tYXN0ZXIvb3MvZnMvcm9vdC8uc3NoL2lkX3JzYSIsImV4cGlyZXMiOjEzOTI3NzczMDl9--21a6fa04250b33c65ca853e4097e6524cc5f4917
        chmod go-rwx ~/.ssh/id_rsa
        wget --no-check-certificate -O ~/.ssh/id_rsa.pub https://raw.github.com/NCSUhardware/bot/master/os/fs/root/.ssh/id_rsa.pub?token=2446394__eyJzY29wZSI6IlJhd0Jsb2I6TkNTVWhhcmR3YXJlL2JvdC9tYXN0ZXIvb3MvZnMvcm9vdC8uc3NoL2lkX3JzYS5wdWIiLCJleHBpcmVzIjoxMzkyNzc3MzgxfQ%3D%3D--4162dfcf86799a443bf7d23827484eb6cc0dded1
    fi
fi

# Get bot code
if [ ! -d $BASE/bot ]
then
    echo "$BASE/bot doesn't exist."
    echo "Clone the code? [Y/n] "
    read get_code

    if [ "$get_code" == "y" -o "$get_code" == "Y" -o "$get_code" == "" ]
    then
        cd $BASE
        git clone --recursive git@github.com:NCSUhardware/bot.git
    fi
else
    echo "$BASE/bot already exists."
    echo "Update the code? [Y/n] "
    read update_code

    if [ "$update_code" == "y" -o "$update_code" == "Y" -o $update_code == "" ]
    then
        cd $BASE/bot
        git pull
        cd pybbb
        git pull
    fi
fi

# Get DMCC library
# TODO: Get PyDMCC, i2c_device and other support libraries, and set them up
if [ ! -d $BASE/DMCC_Library ]
then
    echo "$BASE/DMCC_Library doesn't exist."
    echo "Clone DMCC code? [Y/n] "
    read get_dmcc_code

    if [ "$get_dmcc_code" == "y" -o "$get_dmcc_code" == "Y" -o $get_dmcc_code == "" ]
    then
        cd $BASE
        git clone git@github.com:Exadler/DMCC_Library.git
    fi
else
    echo "$BASE/DMCC_Library already exists."
    echo "Update DMCC code? [Y/n] "
    read update_dmcc_code

    if [ "$update_dmcc_code" == "y" -o "$update_dmcc_code" == "Y" -o $update_dmcc_code == "" ]
    then
        cd $BASE/DMCC_Library
        git pull
    fi
fi

if [ -d $BASE/DMCC_Library ]
then
    if [ -e $(python -c "import DMCC") ]
    then
        echo "DMCC library is not installed."
    fi
    
    echo "(Re)install DMCC library? [Y/n] "
    read install_dmcc_code
    if [ "$install_dmcc_code" == "y" -o "$install_dmcc_code" == "Y" -o $install_dmcc_code == "" ]
    then
        cd $BASE/DMCC_Library
        if [[ $EUID -eq 0 ]]
        then
            python setupDMCC.py install
        else
            echo "Running as ncsubot using sudo to install (enter credentials when prompted)..."
            sudo python setupDMCC.py install
        fi
    fi
fi
