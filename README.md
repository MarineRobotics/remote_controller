<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134843035-bf94204a-1e1a-4baa-b05a-0608b420d87e.png"></p>
<p align="center"><© Marine Robotics, LLC></p>

This is a work in progress...

## Contents

- [System Overview](#system-overview)
- [Environment](#environment)
- [Prerequisite](#prerequisite)
- [Run The Software](#run-the-software)
- [Control Interface](#control-interface)

## System Overview

A combination of MOOS-IvP and ROS is used for the boat system. MOOS-IvP is the backseat driver and handles all the user and mission related logic. ROS is used for the front seat. This contains all the low level logic communicating with the boat’s actuators and sensors.

Flowchart:
<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134934079-bc020045-4d39-49ab-9f9b-42817a68920d.png"></p>

## Environment
Operating System: Ubuntu 16.04 LTS or up is required.

ROS: Kinetic or Melodic.

## Prerequisite
#### ROS setup
To install and confiure ROS. Install ROS kinetic or melodic depending on the operating system, create a workspace and configure the environmental variables  (http://wiki.ros.org/ROS/Tutorials/InstallingandConfiguringROSEnvironment).

Some of the ROS nodes require external python libraries like pyserial to be installed. Each of these required packages is defined in that ROS node’s “package.xml”, enabling rosdep to automatically find all dependencies. Make sure you initialize and update rosdep in your workspace (“rosdep init”, “rosdep update”). 

Make sure pyqt is installed:
```
sudo apt-get install python-qt4 pyqt4-dev-tools
```
For Ubuntu 20.04:
```
pip3 install --user pyqt5  
sudo apt-get install python3-pyqt5  
sudo apt-get install pyqt5-dev-tools
sudo apt-get install qttools5-dev-tools
```

## Run the Software

SSH connect to the Pi (make sure IP address is up to date):
```
ssh pi@192.168.1.10
```
Run front seat on the Pi:
```
cd robocat_frontseat/snap_ws
source devel/setup.bash
roslaunch fs_control start_frontseat.launch
```
Run controller from laptop:
```
cd mr_frontseat/snap_ws
source devel/setup.bash
roslaunch remote_controller controller.launch
```
MOOS:
On the Pi:
```
cd moos-ivp-mr/missions/mission_folder
pAntler mission_robocat.moos
```
On laptop:
```
cd moos-ivp-mr/missions/mission_folder
pAntler mission_shore.moos
```
## Control Interface
Manual control is using keys on keyboard as controller:
WS for propeller, QE for sail and AD for rudder

In Boat State section the status will show as payload during MOOS missions
<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134934203-96bc625d-c441-46ac-a2cf-9d8e144e75be.png"></p>
