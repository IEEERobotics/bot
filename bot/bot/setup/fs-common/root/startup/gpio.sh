#!/bin/bash

gpio_sysfs=/sys/class/gpio

load_gpio () {
  num=$1
  if [ ! -e $gpio_sysfs/gpio${num} ]; then
    echo $num > ${gpio_sysfs}/export
  else
    echo "GPIO $num already exported"
  fi
  # GPIO set to in (High-impedence) by default. 
  # Prevents unexpected current draw during startup.
  echo in > ${gpio_sysfs}/gpio${num}/direction
}
