#!/bin/bash

docker run -it --rm \
  --net=host \
  -v ~/robot_cloud_stack/ros_ws:/ros_ws \
  robot-local