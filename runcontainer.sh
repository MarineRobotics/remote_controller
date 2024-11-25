#!/bin/bash

# Default values
ROS_MASTER_URI=http://192.168.1.160:11311
export UID_GID="$(id -u):$(id -g)"
export UID="$(id -u)"

# Parse command line arguments
OPTS=$(getopt -o i:m:n:b:h --long host-ip:,master:,hostname:,rebuild,help -n 'parse-options' -- "$@")

REBUILD=false

if [ $? != 0 ]; then
    echo "Failed parsing options." >&2
    exit 1
fi

eval set -- "$OPTS"

# Create simple function to resolve hostname to IP
resolve_hostname_to_ip() {
    # Resolve hostname to IP
    hostname=$1
    ip=$(getent hosts "$hostname" | awk '{ print $1 }')
    echo "$ip"
}

while true; do
    case "$1" in
        -i | --host-ip)
            ROS_IP="$2"
            shift 2
            ;;
        -m | --master)
            ROS_MASTER_URI="$2"
            shift 2
            ;;
        -r | --master-resolved)
            ROS_MASTER_URI="http://$(resolve_hostname_to_ip "$2"):11311"
            shift 2
            ;;
        -n | --hostname)
            ROS_HOSTNAME="$2"
            shift 2
            ;;
        -b | --rebuild)
            REBUILD=true
            shift
            ;;
        -h | --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -i, --host-ip IP             Set the ROS_IP environment variable"
            echo "  -m, --master URI             Set the ROS_MASTER_URI environment variable"
            echo "  -r, --master-resolved HOST   Resolve hostname to IP and set ROS_MASTER_URI"
            echo "  -n, --hostname HOSTNAME      Set the ROS_HOSTNAME environment variable"
            echo "  -b, --rebuild                Rebuild the Docker container before running"
            echo "  -h, --help                   Display this help message"
            exit 0
            ;;
        --)
            shift
            break
            ;;
        *)
            break
            ;;
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

# Prompt user to continue or exit
read -p "Press Enter to continue, or any other key to exit" -n 1 -r

project=$(basename "$(pwd)")
xhost +local:"${project}_app_1"

# Rebuild container if required
if [ "$REBUILD" = true ]; then
    echo -e "\e[35mRebuilding container...\e[0m"
    docker-compose build
    echo -e "\e[35mCompleted!\e[0m"
fi

echo -e "\e[35mLaunching remote controller GUI...\e[0m"
docker-compose up

xhost -local:"${project}_app_1"
