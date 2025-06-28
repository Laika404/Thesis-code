#!/bin/bash


./hotspot/hotspot_start.sh
if [[$1 == "-test"]]; then
    sudo valgrind mosquitto -c /etc/mosquitto/mosquitto.conf -v
else
    sudo systemctl start mosquitto
fi
