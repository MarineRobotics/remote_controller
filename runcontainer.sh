#!/bin/bash

# Default values
ROS_MASTER_URI=http://192.168.1.160:11311

# Parse command line arguments
OPTS=`getopt -o i:m:h: --long host-ip:,master:,hostname: -n 'parse-options' -- "$@"`

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
        -- ) shift; break ;;
        * ) break ;;
    esac
done

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
echo "Starting Remote Controller..."


docker-compose up
