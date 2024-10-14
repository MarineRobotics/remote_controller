# Use ROS noetic full desktop version as base image
FROM osrf/ros:noetic-desktop-full

# Create workspace variable and set directory
ENV WORKSPACE=/home/app/workspace
WORKDIR $WORKSPACE/src

# Update and install git
RUN apt-get update && apt-get install -y git

# Move all files from the current directory to a new /remote_controller directory
COPY . ./remote_controller

# Clone the repositories and checkout the correct branches
RUN git clone -b python2 https://github.com/MarineRobotics/mr_messages.git

RUN ls -la

# Navigate back to the workspace drectory
WORKDIR $WORKSPACE

# Create the user
ARG USERNAME=mrdev
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Give the user ownership of the workspace
RUN chown -R $USERNAME:$USERNAME $WORKSPACE
# Create /.ros directory and give user ownership
RUN mkdir /.ros && chown -R $USERNAME:$USERNAME /.ros

USER $USERNAME

# Install ROS dependencies and bild the workspace
RUN /bin/bash -c 'cd ${WORKSPACE} && pwd && . /opt/ros/noetic/setup.bash && rosdep update && rosdep install --from-paths src --ignore-src -r -y'
RUN /bin/bash -c 'cd ${WORKSPACE} && . /opt/ros/noetic/setup.bash && catkin_make'
# Entrypoint to launch remote controller launch file on launch

# Source workspace and launch remote controller launch file
ENTRYPOINT ["/bin/bash", "-c", "source /home/app/workspace/devel/setup.bash && roslaunch remote_controller controller.launch"]
