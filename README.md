<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134843035-bf94204a-1e1a-4baa-b05a-0608b420d87e.png"></p>
<p align="center"><© Marine Robotics, LLC></p>

This is a work in progress...

# Contents

- [Contents](#contents)
- [Operating system requirements](#operating-system-requirements)
- [Local Machine Setup](#local-machine-setup)
  - [Automatic installation](#automatic-installation)
  - [Manual installation](#manual-installation)
    - [Install and configure ROS](#install-and-configure-ros)
    - [Download and build remote controller](#download-and-build-remote-controller)
- [Run the software](#run-the-software)
  - [Start the frontseat on the sailboat](#start-the-frontseat-on-the-sailboat)
  - [Start the remote controller](#start-the-remote-controller)
  - [Run MOOS](#run-moos)
- [Control Interface overview](#control-interface-overview)
- [Software structure overview](#software-structure-overview)


# Operating system requirements
Operating System: Ubuntu 20.04 LTS is required.  

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
  If you look in your current directory you should now have a 'build' and 'devel' folder. Inside the 'devel' folder you can see that there are now several setup.sh files. Sourcing any of these files will overlay this workspace on top of your environment. 
  
* Before continuing source your new setup.sh file:
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
  $ git clone https://github.com/MarineRobotics/remote_controller.git
  ```

  To run correctly, our ROS node requires external libraries like pyqt to be installed. Each of these required packages is defined in that ROS node’s “package.xml”. By using rosdep we can automatically find and install these dependencies.  
  `Rosdep should have been initialized during the install part of this tutorial. If you didn't already do so, do it now:`
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
Password:
```
hovergroup123
```
Run front seat on the Pi:
```
cd robocat_frontseat/snap_ws
source devel/setup.bash
roslaunch fs_control start_frontseat.launch
```

## Start the remote controller
**Make sure the software is up to date**
```
$ cd ~/catkin_ws \
  && git -C src/remote_controller/ pull \
  && git -C src/mr_messages/ pull
```
Run controller from your laptop:
```
$ cd ~/catkin_ws/src/remote_controller
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
Manual control allows you to use keyboard keys to control the boat.
Rudder is moved in 5 degree increments per keypress. The amount of degrees can be modified using the "key increments" setting (field 5)
<p align="center"><img src="https://user-images.githubusercontent.com/3636101/174156119-557d7ade-e87b-4f40-932a-00a36c643b8e.png" height="50%"/></p>

When running the remote controller, the interface will look like the screenshot below.
We describe some of the most immportant features:
![GUI screenshot v2](https://user-images.githubusercontent.com/3636101/174156105-16fea390-25a8-4a45-9d97-0c1d29a99d18.png)


1. Enabling manual mode is necessary to use the remote controller. This will put control into your hands and results in the boat ignoring any payload messages even if a MOOS mission was running.
2. Turns propeller on/off
3. Works best in combination with "Vessel Heading" setting. When enabled, the boat will choose the best sail angle for the current/desired heading. If you go into the wind, or slow down too much during a tack it will automatically turn on the prop to help out. 
4. 
   - Sail heading: ask the sail to hold a specific compass heading, independent of vessel
   - Sail angle: ask the sail to set a specific angle relative to the boat
   - Sail angle of attack : ask the sail to set a specific angle relative to the apparent wind
5. Change the amount of degrees with which the rudder moves for each A/D keypress. For your information: the rudder range is -40 to 40 degrees
6. The current rudder position
7. The desired rudder position, this shows you what you are asking the rudder to do.
8. Motor controller status. In this example 1 is connected (green) and one is not connected. You need both controllers to be green to operate the boat.
9. Stop all actuators from moving.



# Software structure overview

A combination of MOOS-IvP and ROS is used for the boat system. MOOS-IvP is the backseat driver and handles all the user and mission related logic. ROS is used for the front seat. This contains all the low level logic communicating with the boat’s actuators and sensors.

Flowchart:
<p align="center"><img src="https://user-images.githubusercontent.com/3636101/173442644-0efb1272-4638-4f26-963b-9246db97c59b.png"></p>
