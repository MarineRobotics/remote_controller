<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134843035-bf94204a-1e1a-4baa-b05a-0608b420d87e.png"></p>
<p align="center"><© Marine Robotics, LLC></p>

This is a work in progress...

# Contents

- [Software Overview](#software-overview)
- [Operating System requirements](#operating-system-requirements)
- [Local Machine Setup](#local-machine-setup)
- [Run The Software](#run-the-software)
- [Control Interface](#control-interface)

# Software Overview

A combination of MOOS-IvP and ROS is used for the boat system. MOOS-IvP is the backseat driver and handles all the user and mission related logic. ROS is used for the front seat. This contains all the low level logic communicating with the boat’s actuators and sensors.

Flowchart:
<p align="center"><img src="https://user-images.githubusercontent.com/3636101/173442644-0efb1272-4638-4f26-963b-9246db97c59b.png"></p>

# Operating system requirements
Operating System: Ubuntu 20.04 LTS is required.  
:information_source: If you are running an older version, please go to the [Python 2 branch of the software](https://github.com/MarineRobotics/remote_controller/tree/developer)

ROS: Noetic.

# Local Machine Setup

## Automatic installation
[comment]: <> (TODO: Need to tell people to use correct script)
## Manual installation
### Install and configure ROS
* Click the link below to the official ROS tutorial. Follow the tutorial to install ROS Noetic and configure your ~/.bashrc file. Make sure to **install the `desktop` package** or higher depending on the operating system.
http://wiki.ros.org/noetic/Installation/Ubuntu  

* Next we'll install extra python3 related dependencies
   ```
   $ apt-get update
   $ apt-get install python3-catkin-tools python3-osrf-pycommon python3-pip
   ```
* Let's create and build a catkin workspace:
  ```
  $ mkdir -p ~/catkin_ws/src
  $ cd ~/catkin_ws/
  $ catkin build
  ```
  If you look in your current directory you should now have a 'build' and 'devel' folder. Inside the 'devel' folder you can see that there are now several setup.*sh files. Sourcing any of these files will overlay this workspace on top of your environment. 
  
* Before continuing source your new setup.*sh file:
  ```
  $ source devel/setup.bash
  ```

* To make sure your workspace is properly overlayed by the setup script, make sure ROS_PACKAGE_PATH environment variable includes the directory you're in.
  ```
  $ echo $ROS_PACKAGE_PATH
  ```

### Download and build remote controller

* Navigate to your newly created ros workspace
  ```
  $ cd ~/catkin_ws/src
  ```

* Clone the necessary packages using git
  ```
  $ git clone -b python3 https://github.com/MarineRobotics/mr_messages.git
  $ git clone -b python3 https://github.com/MarineRobotics/movement_controls.git
  $ git clone https://github.com/MarineRobotics/remote_controller.git
  ```

  To run correctly, our ROS node requires external libraries like pyqt to be installed. Each of these required packages is defined in that ROS node’s “package.xml”. By using rosdep we can automatically find and install these dependencies.  
  `Rosdep should have been initialized during the install part of this tutorial. If you didn't already dot it now:`
  ```
  $ rosdep init
  $ rosdep update
  ```

* Install all dependencies:
  ```
  $ cd ~/catkin_ws
  $ rosdep install -y \
           --from-paths \
           src \
           --ignore-src
  ```

* Finally, build the remote controller software:
  ```
  $ catkin build
  ```


# Run the software

## Start the frontseat on the sailboat



SSH connect to the front-seat RPi (IP address may change depending on your setup):
```
ssh pi@192.168.1.160
```
Run front seat on the Pi:
```
cd robocat_frontseat/snap_ws
source devel/setup.bash
roslaunch fs_control start_frontseat.launch
```

## Start the remote controller
Run controller from your laptop:
```
$ cd catkin_ws/src/remote_controller
$ ./run.sh
```
## Run MOOS

**On the Pi:**

:information_source: **Manual control must be disabled before executing the pAntler command**  
This is a bug that will be fixed soon, but right now a moos mission can only be started if manual control was not enabled. It is ok for the remote control software to be running, just not for it to be enabled using the "enable manual" button.

```
cd moos-ivp-mr/missions/mission_folder
pAntler mission_robocat.moos
```
**On your laptop:**
```
cd moos-ivp-mr/missions/mission_folder
pAntler mission_shore.moos
```

# Control Interface overview
Manual control is using keys on keyboard as controller:
WS for propeller, QE for sail and AD for rudder

In Boat State section the status will show as payload during MOOS missions
<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134934203-96bc625d-c441-46ac-a2cf-9d8e144e75be.png"></p>
![ROS architecture](https://user-images.githubusercontent.com/3636101/138930940-ef8233cf-61be-4b09-9d52-0d364ddd69f7.png)
