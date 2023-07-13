#!/bin/bash

# Default values
ROS_MASTER_URI=http://192.168.1.160:11311
export UID_GID="$(id -u):$(id -g)"
export UID="$(id -u)"
# Parse command line arguments
OPTS=`getopt -o i:m:h:b --long host-ip:,master:,hostname:,rebuild -n 'parse-options' -- "$@"`

REBUILD=false

if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi

eval set -- "$OPTS"

while true; do
# The case statement inside the loop checks the current argument ($1). 
# If the argument matches one of the option patterns (-ip, --host-ip, -m, --master, -h, --hostname), 
# it sets the corresponding variable to the value of the next argument ($2), 
# then it uses shift; shift; to remove these two arguments (option and its value) from the list and move on to the next pair.
    case "$1" in
        -i | --host-ip ) ROS_IP="$2"; shift; shift ;;
        -m | --master ) ROS_MASTER_URI="$2"; shift; shift ;;
        -h | --hostname ) ROS_HOSTNAME="$2"; shift; shift ;;
        -b | --rebuild ) REBUILD=true; shift ;;
        -- ) shift; break ;;
        * ) break ;;
    esac
done

# Print rebuild flag in purple
echo -e "\e[35mRebuild: $REBUILD\e[0m"

if [ -z "$ROS_HOSTNAME" ] && [ -z "$ROS_IP" ]; then
    export ROS_HOSTNAME=$(hostname)
fi

if [ -n "$ROS_IP" ]; then
    export ROS_IP
fi

if [ -n "$ROS_HOSTNAME" ]; then
    export ROS_HOSTNAME
fi
export ROS_MASTER_URI

# Echo out the values for verification
echo "Remote Controller will start with the following values:"
echo "ROS_IP: $ROS_IP"
echo "ROS_HOSTNAME: $ROS_HOSTNAME"
echo "ROS_MASTER_URI: $ROS_MASTER_URI"

# Ask enter to continue, or any other key to exit
read -p "Press enter to continue, or any other key to exit" -n 1 -r

project=$(basename $(pwd))
xhost +local:${project}_app_1

# Rebuild container if required
if [ "$REBUILD" = true ] ; then
    echo -e "\e[35mRebuilding container...\e[0m"
    docker-compose build
    echo -e "\e[35mCompleted!\e[0m"
fi
echo -e "\e[35mLaunching remote controller GUI...\e[0m"
docker-compose up

xhost -local:${project}_app_1
