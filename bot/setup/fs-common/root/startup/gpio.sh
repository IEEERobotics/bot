#!/bin/bash

gpio_sysfs=/sys/class/gpio

load_gpio () {
  num=$1
  if [ ! -e $gpio_sysfs/gpio${num} ]; then
    echo $num > ${gpio_sysfs}/export
  else
    echo "GPIO $num already exported"
  fi
  echo out > ${gpio_sysfs}/gpio${num}/direction
  echo 0 > ${gpio_sysfs}/gpio${num}/value
}
