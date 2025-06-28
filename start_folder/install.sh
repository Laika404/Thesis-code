#!/bin/bash

sudo apt update
sudo apt install mosquitto mosquitto-clients

# install the mosquitto broker
if ! command -v mosquitto >/dev/null 2>&1; then
    echo "problems with installing mosquitto"
    exit 1
fi

# stop the mosquitto broker
sudo systemctl disable mosquitto
sudo systemctl stop mosquitto


# mosquitto development c libraries
sudo apt install libmosquitto-dev
sudo apt install mosquitto-dev

# gateway client dependencies
sudo apt-get install libpaho-mqttpp3 libpaho-mqttpp-dev


# copy user config for 
sudo cp ./user.conf /etc/mosquitto/conf.d/user.conf

# make a plugins directory
sudo mkdir /etc/mosquitto/plugins

# make binaries for plugin and Gateway client
sudo ./../mqtt_plugin/plugin_refresh.sh
sudo ./../gateway_client/mqtt_client_run.sh

