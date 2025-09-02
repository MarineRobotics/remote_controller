#!/bin/bash

# cd to main ros folder, 2 levels up
cd ../..
source install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///$(pwd)/src/remote_controller/resource/cyclonedds.xml  
ros2 run remote_controller remote_controller
