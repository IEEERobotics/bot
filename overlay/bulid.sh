#!/bin/bash

echo "Compliling the overlay from .dts to .dtbo"

dtc -O dtb -o bb_motor_cape-00A0.dtbo -b O -@ gpio.dts
