#!/bin/bash

echo "Populating filesystem..."
chown -R root.root fs-*
echo "  common files"
rsync -va fs-common/* /
update-rc.d bbb defaults

if [ "$1" == "bot" ]; then
    echo "  bot-only files"
    rsync -va fs-bot/* /
    update-rc.d masquerade defaults

    echo Enabling uplink...
    ifup wlan1
    echo

    echo "Updating packages for hostap..."
    export DEBIAN_FRONTEND=noninteractive
    DPKG_OPTS=Dpkg::Options::="--force-confold"
    apt-get update
    apt-get -y purge udhcpd
    apt-get -y -o ${DPKG_OPTS} install hostapd dnsmasq
fi
