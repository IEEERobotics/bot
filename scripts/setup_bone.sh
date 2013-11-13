#!/usr/bin/env bash
# Install standard software, do git configuration

EX_USAGE=64

# Each should only contain the packages that are added at that level
light="git python-yaml libzmq-dev python-zmq"
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

# Add user ncsubot
if [[ $EUID -e 0 ]]
then
    echo -n "You ran this as root. Setup ncsubot account? [Y/n] "
    read setup_ncsubot

    if [ "$setup_ncsubot" == "Y" -o "$setup_ncsubot" == "y" ]
    then
        # Create user account
        adduser ncsubot

        # Add user to sudoers
        echo "An editor is about to open. Append the following line (copy/paste):"
        echo "ncsubot ALL=(ALL:ALL) ALL"
        echo "Save and exit when you're done. Hit enter to continue."
        read blah
        visudo
        
        # TODO: Add SSH key
    fi
fi

# Configure git
echo "Configuring git..."
if [[ $EUID -e 0 ]]
then
    echo "You ran this as root, changing user to ncsubot..."
    su ncsubot
fi

git config --global user.name "ncsubot"
git config --global user.email "ncsubot@gmail.com"

# Get bot code
if [ ! -f /home/ncsubot/bot ]
then
    echo "/home/ncsubot/bot doesn't exist."
    echo "Clone the code? [Y/n] "
    read get_code

    if [ "$get_code" == "y" -o "$get_code" == "Y" -o $get_code == ""]
    then
        if [[ $EUID -e 0 ]]
        then
            echo "You ran this as root, changing user to ncsubot..."
            su ncsubot
        fi

        cd /home/ncsubot
        git clone --recursive git@github.com:NCSUhardware/bot.git
    fi
else
    echo "/home/ncsubot/bot already exists."
    echo "Update the code? [Y/n] "
    read update_code

    if [ "$update_code" == "y" -o "$update_code" == "Y" -o $update_code == ""]
    then
        if [[ $EUID -e 0 ]]
        then
            echo "You ran this as root, changing user to ncsubot..."
            su ncsubot
        fi

        cd /home/ncsubot/bot
        git pull
        cd pybbb
        git pull
    fi
fi

# Get DMCC library
if [ ! -f /home/ncsubot/DMCC_Library ]
then
    echo "/home/ncsubot/DMCC_Library doesn't exist."
    echo "Clone DMCC code? [Y/n] "
    read get_dmcc_code

    if [ "$get_dmcc_code" == "y" -o "$get_dmcc_code" == "Y" -o $get_dmcc_code == ""]
    then
        if [[ $EUID -e 0 ]]
        then
            echo "You ran this as root, changing user to ncsubot..."
            su ncsubot
        fi

        cd /home/ncsubot
        git clone git@github.com:Exadler/DMCC_Library.git
    fi
else
    echo "/home/ncsubot/DMCC_Library already exists."
    echo "Update DMCC code? [Y/n] "
    read update_dmcc_code

    if [ "$update_dmcc_code" == "y" -o "$update_dmcc_code" == "Y" -o $update_dmcc_code == ""]
    then
        if [[ $EUID -e 0 ]]
        then
            echo "You ran this as root, changing user to ncsubot..."
            su ncsubot
        fi

        cd /home/ncsubot/DMCC_Library
        git pull
    fi
fi

if [ -f /home/ncsubot/DMCC_Library ]
then
    if [ -e $(python -c "import DMCC") ]
    then
        echo "DMCC library is not installed."
    fi
    
    echo "(Re)install DMCC library? [Y/n] "
    read install_dmcc_code
    if [ "$install_dmcc_code" == "y" -o "$install_dmcc_code" == "Y" -o $install_dmcc_code == ""]
    then
        cd /home/ncsubot/DMCC_Library
        if [[ $EUID -e 0 ]]
        then
            python setupDMCC.py install
        else
            echo "Running as ncsubot using sudo to install (enter credentials when prompted)..."
            sudo python setupDMCC.py install
        fi
    fi
fi
