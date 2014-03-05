#!/bin/bash

dir=$(dirname $0)
source $dir/slots.sh

enable_adcs() {
  load_slot cape-bone-iio
}

