#!/bin/bash

dir=$(dirname $0)
source $dir/pwm.sh
source $dir/gpio.sh
source $dir/adc.sh

# Drive motor 0: P9_31 (pwm0/ehr0A), P9_25 (gpio117)
load_pwm     0
set_period   0 1000000
set_duty     0  250000
set_polarity 0 0
load_gpio 117

# Drive motor 1: P9_29 (pwm1/ehr0B), P9_27 (gpio115)
load_pwm     1
set_period   1 1000000
set_duty     1  250000
set_polarity 1 0
load_gpio 115

# Drive motor 2: P8_19 (pwm5/ehr2B), P8_15 (gpio47)
load_pwm     5
set_period   5 1000000
set_duty     5  250000
set_polarity 5 0
load_gpio 47

# Drive motor 3: P8_13 (pwm6/ehr2A), P8_11 (gpio45)
load_pwm     6
set_period   6 1000000
set_duty     6  250000
set_polarity 6 0
load_gpio 45

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

# Turret servo - pan: P9_42 (pwm2/ecap0)
load_pwm     2
set_period   2 20000000  # 20ms, standard servo period
set_duty     2  1500000  # 1.5ms, standard neutral point
set_polarity 2 0
run_pwm      2  # zero the servo on setup

# Turret servo - tilt: P9_28 (pwm7/ecap2)
load_pwm     7
set_period   7 20000000  # 20ms, standard servo period
set_duty     7  1500000  # 1.5ms, standard neutral point
set_polarity 7 0
run_pwm      7  # zero the servo on setup

#9.12  GPIO1[28] = gpio60   Motor1
#9.13  GPIO0[31] = gpio31   Motor2
#9.25  GPIO3[21] = gpio117  Motor3
#9.27  GPIO3[19] = gpio115  Motor4

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

enable_adcs
