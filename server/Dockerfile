FROM ros:indigo-robot

RUN apt-get update && apt-get install -y \
    python-twisted \
    ros-indigo-freenect-launch \
    ros-indigo-hokuyo-node \
    ros-indigo-kobuki-core \
    ros-indigo-kobuki-node \
    ros-indigo-rosbridge-suite \
    wget \
    && rm -rf /var/lib/apt/lists/

RUN wget https://raw.githubusercontent.com/davidlandry93/glo7021/master/server/robmob.launch

RUN ./ros_entrypoint.sh && rosrun kobuki_ftdi create_udev_rules

EXPOSE 9090

CMD ["roslaunch", "robmob.launch"]
