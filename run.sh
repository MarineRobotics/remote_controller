#!/bin/bash


# TODO: allow pi address to be specified as variable. Keep .160 as default
# TODO: allow host ip to be specified as variable, don't look for it if that's the case

# Get list of host ip addresses
# Find ip where network-id (192.168.1) matches the boat network id
# Use the boat network one as ros hostname
# Show error if there is none
# Allow boat network to be given as variable in case it changed
iplist=$(hostname -I)
for ip in $iplist
do
    # extract up to last dot. cutting off host id. 
    # This assumes the subnet is 255.255.255.0
    netId=${ip%.*}
    if [ "$netId" == "192.168.1" ]; then
        hostIP=$ip
    fi
    # check if i is right ip address
done
# End script if we did could not assign hostIP
if [ -z ${hostIP+x} ]; then
  echo "could not find host ip, are you connected to the boat network?"
  exit 1
fi

echo "found host ip = ${hostIP}"
export ROS_MASTER_URI=192.168.1.160:11311
export ROS_HOSTNAME=$hostIP

# source ROS workspace
source ../../devel/setup.bash

# launch remote controller
roslaunch remote_controller controller.launch 
