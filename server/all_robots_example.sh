#!/bin/bash

for ip in 192.168.0.{100..114}
do
    echo "Starting on ${ip}"
    ssh -t robmob@${ip} "
    sudo apt-get install --yes --force-yes \
         nload \
         ros-indigo-compressed-image-transport && \
    sudo wget -p /opt/ros/indigo/share/kobuki_node/launch https://github.com/davidlandry93/glo4001/blob/master/server/robmob.launch && \
    sudo bash -c "curl -sSf https://raw.githubusercontent.com/davidlandry93/glo4001/master/server/robmob.launch > /opt/ros/indigo/share/kobuki_node/launch/robmob.launch""
done
echo "Done."
