#!/bin/bash

echo "Updating packages..."
apt-get purge udhcpd
apt-get install hostapd dnsmasq vim
echo
echo "Populating files..."
rsync -va fs/* /

echo "Running depmod..."
# pick up new modules in /lib/modules
depmod -a
