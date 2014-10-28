#!/bin/bash

dir=$(dirname $0)
source $dir/slots.sh
source $dir/pwm.sh
source $dir/gpio.sh
source $dir/adc.sh

# Gun laser: P8_35 (gpio8)
load_gpio 8

# Gun motor - left: P8_37 (gpio78)
load_gpio 78

# Gun motor - right: P8_39 (gpio76)
load_gpio 76

# Gun trigger - retract: P8_41 (gpio74)
load_gpio 74

# Gun trigger - advance: P8_43 (gpio72)
load_gpio 72

# Turret servo - pan/yaw: P9_42 (pwm2/ecap0)
load_pwm     2
set_period   2 20000000  # 20ms, standard servo period
set_duty     2  1500000  # 1.5ms, standard neutral point
set_polarity 2 0
run_pwm      2  # zero the servo on setup

# Turret servo - tilt/pitch: P9_16 (pwm4/EHR1B)
load_pwm     4
set_period   4 20000000  # 20ms, standard servo period
set_duty     4  1500000  # 1.5ms, standard neutral point
set_polarity 4 0
run_pwm      4  # zero the servo on setup

# Color sensor LED (50%): P8_19 (pwm5/EHR2A)
load_pwm     5
set_period   5 20000000
set_duty     5 10000000 
set_polarity 5 0
run_pwm      5  

# IR sensor array MUX select lines
load_gpio 44  # P8_12
load_gpio 26  # P8_14
load_gpio 46  # P8_16
load_gpio 65  # P8_18

# IR analog input GPIOs
load_gpio 39  # P8_04, front
load_gpio 67  # P8_06, back
load_gpio 68  # P8_08, left
load_gpio 35  # P8_10, right

# Ultrasonic GPIOs
load_gpio 117  # P9_25 front trigger
load_gpio 49   # P9_23 front echo
load_gpio 45   # P8_11 back trigger
load_gpio 47   # P8_15 back echo
load_gpio 112  # P9_30 left trigger
load_gpio 113  # P9_28 left echo
load_gpio 111  # P9_29 right trigger
load_gpio 110  # P9_31 right echo

enable_adcs
load_slot BB-BONE-PRU-01
