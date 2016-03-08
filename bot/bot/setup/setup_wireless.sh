#!/bin/bash
# Install standard software, do git configuration
# https://learn.adafruit.com/setting-up-wifi-with-beaglebone-black/overview

sudo apt-get update && apt-get -y upgrade

sudo apt-get -y install wireless-tools usbutils

sudo apt-get -y install firmware-atheros

sudo wget http://linuxwireless.org/download/htc_fw/1.3/htc_9271.fw

sudo cp htc_9271.fw /lib/firmware

rsync -va fs-bot/* /


ntpdate -b -s -u pool.ntp.org
apt-get update && apt-get install git
git clone https://github.com/adafruit/wifi-reset.git
cd wifi-reset
chmod +x install.sh
./install.sh
