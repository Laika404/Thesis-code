#!/bin/bash
g++ -o mqtt_client mqtt_client.cpp -lpaho-mqttpp3 -lpaho-mqtt3a
cp ./mqtt_client ./../experiment_code/mqtt_client
