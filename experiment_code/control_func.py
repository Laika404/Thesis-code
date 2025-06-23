# file which contains the class that represents a MQTT controller client as described in the thesis

import paho.mqtt.client as mqtt
import json
import copy



start_topic = "exp/start"
stop_topic = "exp/stop"
check_topic = "exp/check"
broker_address = {"ip" : "192.168.42.1", "port": 1883}

# the messages the client sends in json format
default_start = {
            "tp": "sta",
            "t": 2_000,
            "hz": 5,
            "ps": 10,
            "qts": 0,
            "ct":0
        }
default_stop = {
    "tp": "sto"
}
default_off = {
    "tp": "off"
}


class ExperimentClient: 
    def __init__(self):
        # start client
        self._client = None
        self._json = copy.copy(default_start)

    def startup_client(self):
        self._client = mqtt.Client()
        if self._client.connect(broker_address["ip"], broker_address["port"], 60) != 0:
            raise ValueError("client did not connect")
        self._client.loop_start()

    def send_start(self):
        self._client.publish(start_topic, json.dumps(self._json), 2)

    def send_stop(self):
        self._client.publish(stop_topic, json.dumps(default_stop), 2)

    def send_off(self):
        self._client.publish(start_topic, json.dumps(default_off), 2)
    
    def send_check(self):
        self._client.publish(check_topic, json.dumps(default_off), 2)




    def new_config(self, config):
        self._json = copy.copy(config)
    
    def get_config(self):
        return copy.copy(self._json)
    
    # change a single value
    def change_single(self, name, val):
        self._json[name] = val

    # stops the client and exits the program
    def end_all(self):
        self._client.loop_stop()
        exit(0)
    
    # determines the file name of the data if the configuration was used this client holds
    def file_name_con(self, con="", am_units=1, wifi=None):
        if con=="":
            con = self._json
        if wifi != None:
            return f"{con["t"]}_{con["hz"]}_{con["ps"]}_{con["qts"]}_{con["ct"]}_{am_units}_{wifi}.csv"
        else:
            return f"{con["t"]}_{con["hz"]}_{con["ps"]}_{con["qts"]}_{con["ct"]}_{am_units}.csv"