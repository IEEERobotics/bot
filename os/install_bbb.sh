#!/bin/bash

echo "Populating filesystem..."
chown -R root.root fs
rsync -va fs/* /

#cat /dev/null > /etc/udev/rules.d/70-persistent-net.rules

echo
echo Enabling uplink...
ifup wlan1

echo
echo "Updating packages..."

export DEBIAN_FRONTEND=noninteractive
DPKG_OPTS=Dpkg::Options::="--force-confold"

apt-get update
apt-get -y purge udhcpd
apt-get -y -o ${DPKG_OPTS} install hostapd dnsmasq

update-rc.d masquerade defaults

