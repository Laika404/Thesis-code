#!/bin/bash
gcc -fPIC -shared -I/usr/include/mosquitto -o message_logger.so message_logger.c -lmosquitto
sudo cp ./message_logger.so /etc/mosquitto/plugins/
sudo chmod 755 /etc/mosquitto/plugins/message_logger.so
