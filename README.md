<p align="center"><img src="https://user-images.githubusercontent.com/47678311/134843035-bf94204a-1e1a-4baa-b05a-0608b420d87e.png"></p>
<p align="center">© Marine Robotics, LLC</p>

This is a work in progress. There is now a script available to run the Remote Controller, which is the recommended method. The manual setup steps are still available for those who wish to install from source.


# Contents

- [Introduction](#introduction)
- [Operating System Requirements](#operating-system-requirements)
- [Running the Remote Controller](#running-the-remote-controller)
- [Launching the System](#launching-the-system)
  - [Start the frontseat on the sailboat](#start-the-frontseat-on-the-sailboat)
  - [Start the remote controller](#start-the-remote-controller)
  - [Run MOOS](#run-moos)
- [Control Interface Overview](#control-interface-overview)
- [Setup System from Source](#setup-system-from-source)
- [Software Structure Overview](#software-structure-overview)



# Introduction
This user manual provides instructions on how to connect to and control a boat using a Docker-based ROS application. The application is started using a script, and you provide information about the boat as command-line arguments.




# Launching the System

This section provides instructions on how to start the boat, launch the remote controller and run MOOS.

## Prerequisites
### Windows
1. Install [Docker Desktop](https://docs.docker.com/docker-for-windows/install/)
2. [Follow the VcXsrv installation instructions](#enable-docker-gui-support-on-windows)
### Ubuntu
1. Install [Docker engine](https://docs.docker.com/engine/install/ubuntu/)
2. Install Docker Compose
    ```
    sudo apt install docker-compose
    ```
### Finally
1. Download the current repository from GitHub
    ```bash
    git clone -b python3 https://github.com/MarineRobotics/remote_controller.git
    ```

Make sure these are installed and properly configured on your system before proceeding.

## Start the frontseat on the sailboat

SSH connect to the front-seat RPi (IP address may change depending on your setup):

```bash
ssh pi@192.168.1.160
```

Password:

```bash
hovergroup123
```

Run front seat on the Pi:

```bash
$ launch_frontseat.sh
```

:information_source: **important: shutting down**  
  press ctrl + c once and wait for the sequence to finish automatically. This can take up to around a minute.

## Start the Remote Controller
**On your laptop**, navigate to the `remote_controller` directory and run the script:
### Ubuntu
```bash
./runcontainer.sh -h ${HOST}.local -m http://192.168.1.160:11311
```
### Windows
:information_source: Make sure XLaunch is running before executing the script.  
Launch the script from Powershell, not from "cmd".
```powershell
.\runwindows.ps1
```


The script accepts the following command-line arguments:

- `--host-ip <ip>` or `-i <ip>`: Use this to specify the **IP address of your laptop**. If you do not specify one, the script will attempt to automatically retrieve it.
- `--hostname <hostname>` or `-h <hostname>`: Use this to specify the **hostname of your laptop**. This is the name that the boat will use to connect to your laptop. If you do not specify one, the script will attempt to automatically retrieve it, and is an alternative to `--host-ip`.
- `--master <ip>` or `-m <uri>`: Use this to specify the IP of the ROS Master, normally the **boat IP**. This sets the `ROS_MASTER_URI` environment variable to `<uri>`. If not provided, it defaults to `http://192.168.1.160:11311`.

**Note**: You only need to provide one of `--host-ip` or `--hostname`, not both. In most cases, the `--master` URI will be the IP address of the boat.

Here is an example of running the script with command-line arguments:

Ubuntu:
```bash {id="python-print" class="blue large" data-filename="test.py"}
./runcontainer.sh -h mrdev.local -m http://192.168.1.160:11311
```
Windows:
```powershell
.\runwindows.ps1 -h mrdev -m http://192.168.1.160:11311
```

In this example, `192.168.1.100` is the IP address of the boat. The script will echo out the values of `ROS_IP`, `ROS_HOSTNAME`, and `ROS_MASTER_URI` for verification before starting the Docker service and connecting to the boat.


## Run MOOS

**On the Pi:**

:information_source: **Manual control must be disabled before executing the pAntler command**  
A moos mission can only be started if manual control was not enabled. It is ok for the remote control software to be running, just not for it to be enabled using the "enable manual" button.

```bash
cd moos-ivp-mr/missions/mission_folder
pAntler mission_robocat.moos
```

**On your laptop:**

```bash
cd moos-ivp-mr/missions/mission_folder
pAntler mission_shore.moos
```

# Enable docker GUI support on Windows

**Install VcXsrv Windows X Server** to enable the GUI to be displayed on Windows.
## Installation

1. Download the installer from the official VcXsrv Windows X Server website. Here is the link: https://sourceforge.net/projects/vcxsrv/

2. Run the installer. It is a straightforward process: just accept the license, select the install location, and then install.

## Configuration

1. After installing, launch the XLaunch application.

2. A series of windows will appear for configuration options. In the `Display settings`, you can leave the default settings (Multiple windows) and click `Next`.

3. In the `Client startup` screen, select `Start no client` and click `Next`.

4. In the `Extra settings` window, check `Disable access control`. This is necessary to allow Docker containers to connect to the X server. Note: this does reduce the security of the X server, so be sure you understand the implications of this, especially if you are on a shared network.

## Saving XLaunch Configuration

1. Before you click `Finish` in the final step of the configuration process, you can save your configuration by clicking on `Save configuration`. 
2. Save the configuration file (which has an `.xlaunch` extension) somewhere convenient.
3. In the future, **you can start VcXsrv with the same settings by simply double-clicking this `.xlaunch` file.**
4. Finally, click `Next` and then `Finish` to launch the X server.

[Click here](#prerequisites) To navigate back to the remote controller launch instructions

# Control Interface Overview

Manual control allows you to use keyboard keys to control the boat.
Rudder is moved in 5 degree increments per keypress. The amount of degrees can be modified using the "key increments" setting (field 5)
<p align="center"><img src="https://user-images.githubusercontent.com/3636101/174156119-557d7ade-e87b-4f40-932a-00a36c643b8e.png" height="50%"/></p>

When running the remote controller, the interface will look like the screenshot below.
We describe some of the most important features:
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

# Setup System from Source

This section provides instructions on how to setup your system from source. These steps
are only necessary for those who wish to install from source.

## Manual installation
### Install ROS
* Click the link below to the official ROS tutorial. Follow the tutorial to install ROS Noetic and configure your ~/.bashrc file. Make sure to **install the `desktop` package** or higher depending on the operating system.
http://wiki.ros.org/noetic/Installation/Ubuntu  
### Install dependencies and configure workspace
* First we'll install extra python3 related dependencies
   ```
   $ sudo apt update
   $ sudo apt install python3-catkin-tools python3-osrf-pycommon python3-pip
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
  $ sudo rosdep init
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

# Software Structure Overview

A combination of MOOS-IvP and ROS is used for the boat system. MOOS-IvP is the backseat driver and handles all the user and mission related logic. ROS is used for the front seat. This contains all the low level logic communicating with the boat’s actuators and sensors.

Flowchart:
<p align="center"><img src="https://user-images.githubusercontent.com/3636101/173442644-0efb1272-4638-4f26-963b-9246db97c59b.png"></p>
