// This file contains the main program loop of the Unit

#include <M5Core2.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "jsonhandler.h"
#include "config.h"
#include "esp_timer.h"

// WiFi credentials
const char* ssid = "MQTT_experiment";
const char* password = "SecurePass123";

// MQTT broker settings
const char* mqtt_server = "192.168.42.1";
const int mqtt_port = 1883;
const char* mqtt_topic = "cur/cur";

// communication with python
const char* mqtt_start = "exp/start";
const char* mqtt_stop = "exp/stop";

// communication with broker plugin
const char* mqtt_start_plugin = "exp/plug_start";
const char* mqtt_stop_plugin = "exp/plug_stop";



WiFiClient espClient;
PubSubClient client(espClient);

// callback in case the MQTT client receives a message
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]:\n");
  
  // Create a string from the payload
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';

    handleJsonMessageStart(message);
    
}

// prints the experiment parameter on the lcd that
void printExpStats(){
  M5.Lcd.setCursor(0, 0);
  M5.lcd.print("duration : ");
  M5.lcd.print((double) Config::tot_time_exp/1000);
  M5.lcd.print("\n frequency : ");
  M5.lcd.print(Config::freq_exp);
  M5.lcd.print("\n payload size : ");
  M5.lcd.print(Config::size_packet_exp);
  M5.lcd.print("\n process time µs : ");
  M5.lcd.print(Config::calc_time);

}


// connects to the local wifi network
void reconnectToWifi(){
  if (WiFi.status() != WL_CONNECTED) {
    Config::start_exp = 0;
    M5.Lcd.fillScreen(TFT_PURPLE);
    Serial.println("Connecting to WiFi");
    WiFi.disconnect(true);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.println(".");
    }
  M5.Lcd.fillScreen(TFT_LIGHTGREY);
  M5.Lcd.println("WiFi connected!");
  Serial.println("\nWiFi connected!");
  }

}

// tries to establish connection
void reconnectMQTT() {
  while (!client.connected()) {
    reconnectToWifi();
    Config::start_exp = 0;
    M5.Lcd.fillScreen(TFT_LIGHTGREY);
    Serial.println("Connecting to MQTT...");
    if (client.connect(WiFi.macAddress().c_str())) {
      M5.Lcd.fillScreen(TFT_BLUE);
      Serial.println("MQTT connected");
      client.subscribe(mqtt_start);
      client.subscribe(mqtt_stop);

    } else {
      Serial.print("Failed, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

// Time Unit needs to stop experiment
long stop_time;
// time in microseconds for frequency
int64_t freq_time;
// amount of send packets
int amount_packets;
// variables used for jitter calculation
int64_t jitter_sum;
int64_t new_delay;
int64_t old_delay;
// Unit has a couple of states associated with start_exp and stop_exp
// start_exp = 0 || Unit is idle
// start_exp = 1 || Start the Unit
// start_exp = 2 || Unit is in the experiment

// stop_exp = 1 || stop any experiment

void experiment_loop(){
  /// stop experiment
    if (Config::stop_exp == 1){
      Config::stop_exp = 0;
      Config:: start_exp = 0;
      M5.Lcd.fillScreen(RED);
      delay(500);
      M5.Lcd.fillScreen(TFT_BLUE);
      return;
    }
  if (Config::start_exp == 0){
    return;
    // start experiment
  } else if (Config::start_exp == 1){
    Config::start_exp = 2;
    // set screen
    M5.Lcd.fillScreen(GREEN);
    printExpStats();
    // set time related variables
    freq_time = (int) ((1.0/ (double) Config::freq_exp)*1000000);
    stop_time = millis() + Config::tot_time_exp;
    // send message to the broker plugin initializing it
    client.publish(mqtt_start_plugin, Config::new_message, PLUGIN_SZ);
    // amount packets is 0 at the start
    amount_packets = 0;
    jitter_sum = 0;
    // set memory message not to \0
    for (int i =0; i <= Config::size_packet_exp; i++){
      if (i == Config::size_packet_exp){
      Config::new_message[i] = '\0'; 
      } else{
        Config::new_message[i] = 'a';
      }
    }
    Serial.println(Config::new_message);
    // start the timer
    stop_time = millis() + Config::tot_time_exp;
  }
  // stay in this loop to save time
  if (Config::start_exp == 2){
    int start_loop_time = millis();
    int q = 1;
    // while(q == 1) {
    while ((millis()-start_loop_time) < 1000) {
      if (millis()> stop_time){
        M5.Lcd.fillScreen(BLUE);
        Config::start_exp = 0;
        // send the total amount of run packets the unit has send after a short delay
        delay(0.2);
        snprintf(Config::new_message, PLUGIN_SZ, "%d,%d", amount_packets, jitter_sum);
        client.publish(mqtt_stop_plugin, Config::new_message, true);
        break;

      }
      static int64_t last_message = 0;
      if (esp_timer_get_time() - last_message > freq_time) {
        last_message = esp_timer_get_time();
        client.publish(mqtt_topic, (uint8_t *) Config::new_message, Config::size_packet_exp, false);
        new_delay = esp_timer_get_time() - last_message;
        amount_packets++;
        if (amount_packets >= 2){
          jitter_sum += abs(new_delay -old_delay);
        }
        old_delay = new_delay;
      }
      q = 0;
    }
  }

}

void setup() {
  M5.begin();
  Serial.begin(115200); // Start serial communication at 115200 baud rate
  M5.Lcd.fillScreen(TFT_PURPLE);
  M5.Lcd.print("Transmitter\n");
  reconnectToWifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  delay(1000); // Wait for 1 second to ensure setup is ready
}
// main program loop
void loop() {
  M5.update();
  // mqtt reconnect
  if (!client.connected()) {
    reconnectMQTT();
    M5.lcd.print("Client connected!\n");
  }
  // mqtt client
  client.loop();

  experiment_loop();
}