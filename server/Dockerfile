FROM ros:indigo-robot

RUN apt-get update && apt-get install -y \
    git \
    python-twisted \
    ros-indigo-hokuyo-node \
    ros-indigo-kobuki-core \
    ros-indigo-kobuki-node \
    ros-indigo-rosbridge-suite \
    && rm -rf /var/lib/apt/lists/

# This needs to be run once so that the computer can speak to the kobuki.
RUN rosrun kobuki_ftdi create_udev_rules

EXPOSE 9090

CMD ["roslaunch", "/opt/ros/indigo/share/rosbridge_server/launch/rosbridge_websocket.launch"]
