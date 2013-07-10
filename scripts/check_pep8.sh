#!/usr/bin/env bash

# Check source file for PEP8 conformance.

pep8 start.py \
     lib/lib.py \
     planner/planner.py \
     driver/driver.py \
     gunner/gunner.py \
     gunner/wheel_gunner.py \
     driver/mech_driver.py \
     localizer/localizer.py \
     follower/follower.py \
     lib/exceptions.py
     
