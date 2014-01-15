#!/bin/bash

echo "Updating packages..."
apt-get purge udhcpd
apt-get install hostapd dnsmasq
echo
echo "Populating files..."
rsync -va fs/* /

update-rc.d masquerade defaults

