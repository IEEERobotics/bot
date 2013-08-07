#!/bin/bash

source pwm.sh
source gpio.sh
source adc.sh

# servo on ecap0
load_pwm 2
set_period 2 10000000
set_duty   2  1924925   # 135 degrees
#set_duty   2  2400000
set_polarity 2 0
run_pwm 2

# IR on ecap2
load_pwm 7
set_period 7 18000
set_duty   7 12000
set_polarity 7 0

# Motor1 on EHRPM1B (pwm4)
load_pwm 4
set_period 4 1000000
set_duty   4  250000
set_polarity 4 0

# Motor2 on EHRPM1A (pwm3)
load_pwm 3
set_period 3 1000000
set_duty   3  250000
set_polarity 3 0

# Motor3 on EHRPM0B (pwm1)
load_pwm 1
set_period 1 1000000
set_duty   1  250000
set_polarity 1 0

#9.12  GPIO1[28] = gpio60   Motor1
#9.13  GPIO0[31] = gpio31   Motor2
#9.25  GPIO3[21] = gpio117  Motor3
#9.27  GPIO3[19] = gpio115  Motor4

load_gpio 60

enable_adcs
