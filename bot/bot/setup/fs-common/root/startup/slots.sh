#!bin/bash

slots=/sys/devices/bone_capemgr.*/slots

load_slot () {
  cat $slots | grep -q $1
  if [ $? -eq 0 ]; then
    echo Module $1 already loaded
  else 
    echo $1 > $slots
  fi
} 

