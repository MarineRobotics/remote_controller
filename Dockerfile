# Use ROS noetic full desktop version as base image
FROM osrf/ros:noetic-desktop-full

# Create workspace variable and set directory
ENV WORKSPACE=/home/app/workspace
WORKDIR $WORKSPACE/src

# Update and install git
RUN apt-get update && apt-get install -y git

# Move all files from the current directory to a new /remote_controller directory
COPY . .

# Clone the repositories and checkout the correct branches
RUN git clone -b python2 https://github.com/MarineRobotics/mr_messages.git

# Navigate back to the workspace drectory
WORKDIR $WORKSPACE

# Install ROS dependencies and bild the workspace
RUN /bin/bash -c '. /opt/ros/noetic/setup.bash; rosdep update; rosdep install --from-paths src --ignore-src -r -y'
RUN /bin/bash -c '. /opt/ros/noetic/setup.bash; catkin_make'

# Entrypoint to launch remote controller launch file on launch

# Source workspace and launch remote controller launch file
ENTRYPOINT ["/bin/bash", "-c", "source /home/app/workspace/devel/setup.bash && roslaunch remote_controller controller.launch"]