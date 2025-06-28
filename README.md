# Unit-to-Gateway code - Bachelor Thesis
#### Maker: Sietse van de Griend
#### Title: Packet Loss in MQTT ProtocolBased Communication for SensorSPHERE
#### Source:  [Thesis](https://scripties.uba.uva.nl/search?id=record_56102)

#### abstract:
The MQTT protocol is a widely used communication protocol in real-world IoT (Internet
of Things) applications, including Wireless Sensor Networks (WSNs). One of the latest
products implementing the MQTT protocol for WSN’s is the currently in development
SensorSPHERE. Aimed at real-time environmental monitoring, the SensorSPHERE collects
large volumes of sensor data through sensor microcontrollers (Units) communicating with
an MQTT broker (Gateway). In preliminary testing the SensorSPHERE team observed
significant packet loss. This thesis aimed at reducing the packet loss by providing insight
into the contribution of four key environmental factors, WiFi signal strength (measured in
SNR), Gateway processing time, message frequency and message size. This was partly done
through examining the critical thresholds where data loss was kept under 5%. The findings
were obtained through a series of quantitative experiments which simulated SensorSPHERE
Unit-To-Gateway behavior with a laptop functioning as Gateway and the M5stack as a
Unit. The results identified critical 5 % data loss thresholds and clear packet loss patterns
for all the environmental factors. Based on these insights, this thesis recommends that the
SensorSPHERE team optimize throughput by increasing message size and reducing message
frequency.




## How to install
The code is made to work on Linux Ubuntu 24.04.2 LTS.
### 1. Run the install script
*WARNING, THIS HAS NOT BEEN TESTED*


(make sure all .sh files have execute permissions)  
Run start_folder/install.sh

### 2. Python depencies
Python code made to work for Python version 3.12.3 64-bit  
These dependencies need to be downloaded manually

| Python dependencies |
|:-------------|
|paho.mqtt.client|
|matplotlib.pyplot|
|Pandas|
|NumPy|
|Patsy|
|SciPy|
|Statsmodels|

### 3. Startup
(use ./start_mqtt.sh -test for test purposes and to see print statements)  
run ./start_mqtt.sh

### 4. Stop
run ./stop_mqtt.sh
