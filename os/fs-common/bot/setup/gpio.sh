#!/bin/bash

#9.12  GPIO1[28] = gpio60   Motor1
#9.13  GPIO0[31] = gpio31   Motor2
#9.25  GPIO3[21] = gpio117  Motor3
#9.27  GPIO3[19] = gpio115  Motor4

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
