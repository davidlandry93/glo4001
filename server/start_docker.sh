#!/bin/sh

docker run --name robmob -i -t --rm -p 0.0.0.0:9090:9090 --device=/dev/ttyACM0 --device=/dev/ttyUSB0 robmob
