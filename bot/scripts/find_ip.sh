#!/usr/bin/env bash
# List IP addresses in noob-friendly format

raw_addrs=`ifconfig | awk -F "[: ]+" '/inet addr:/ { print $4 }'`
set -- $raw_addrs
addrs=( $@ )

for ((i=0;i<${#addrs[@]};++i)); do
    printf "[$i]: %s\n" "${addrs[i]}"
done
