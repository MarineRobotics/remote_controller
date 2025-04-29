# Make sure ROS is installed


# Add ROS to bashrc? Or edit "RUN" script with correct ros location?
# Or do we only need ros location for catkin build?

# Update rosdep and install all required dependencies
rosdep update && \
  rosdep install -y \
  --from-paths \
  src \
  --ignore-src

# Build ROS package
catkin build