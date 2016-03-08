#!/bin/bash

dir=$(dirname $0)
source $dir/slots.sh

pwm_sysfs=/sys/class/pwm

pwm_to_pin[0]=P9_31  # ehr0A
pwm_to_pin[1]=P9_29  # ehr0B
pwm_to_pin[2]=P9_42  # ecap0
pwm_to_pin[3]=P9_14  # ehr1A
pwm_to_pin[4]=P9_16  # ehr1B
pwm_to_pin[5]=P8_19  # ehr2A
pwm_to_pin[6]=P8_13  # ehr2B
pwm_to_pin[7]=P9_28  # ecap2

load_pwm () {
  load_slot am33xx_pwm
  num=$1
  if [ ! -e $pwm_sysfs/pwm${num} ]; then
    echo  $num > $pwm_sysfs/export
    load_slot bone_pwm_${pwm_to_pin[$num]}
  else
    echo "PWM $num already exported"
  fi
  echo 0 > $pwm_sysfs/pwm${num}/run
}

set_duty () {
  echo $2 > $pwm_sysfs/pwm${1}/duty_ns
}

set_period () {
  echo $2 > $pwm_sysfs/pwm${1}/period_ns
}

set_polarity () {
  echo $2 > $pwm_sysfs/pwm${1}/polarity
}

run_pwm () {
  echo 1 > $pwm_sysfs/pwm${1}/run
}

