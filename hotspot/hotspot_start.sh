#!/bin/bash
sudo nmcli connection add type wifi ifname wlo1 con-name my-hotspot autoconnect yes ssid MQTT_experiment

sudo nmcli connection modify my-hotspot wifi-sec.key-mgmt wpa-psk
sudo nmcli connection modify my-hotspot wifi-sec.psk "SecurePass123"

sudo nmcli connection modify my-hotspot 802-11-wireless.mode ap
sudo nmcli connection modify my-hotspot ipv4.method shared
sudo nmcli connection modify my-hotspot ipv4.addresses 192.168.42.1/24

sudo nmcli connection up my-hotspot
