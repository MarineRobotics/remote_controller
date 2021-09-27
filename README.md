<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134843035-bf94204a-1e1a-4baa-b05a-0608b420d87e.png"></p>
<p align="center"><© Marine Robotics, LLC></p>

This is a work in progress...

## Contents

- [System Overview](#system-overview)
- [Environment](#environment)
- [Run The Software](#run-the-software)
- [Control Interface](#control-interface)

## System Overview

A combination of MOOS-IvP and ROS is used for the boat system. MOOS-IvP is the backseat driver and handles all the user and mission related logic. ROS is used for the front seat. This contains all the low level logic communicating with the boat’s actuators and sensors.

Flowchart:
<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134934079-bc020045-4d39-49ab-9f9b-42817a68920d.png"></p>

## Environment
Operating System: Ubuntu 16.04 LTS or up is required
ROS: Kinetic or Melodic

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
