// Used to handle any message in json format
// messages include

// sta : start experiment
// sto : stop experiment
// off : Turn the Unit off

#include <ArduinoJson.h>
#include "config.h"
#include <M5Core2.h>


void handleJsonMessageStart(const char* message) {
  StaticJsonDocument<200> doc; // Adjust size based on your expected JSON
  DeserializationError error = deserializeJson(doc, message);

  if (error) {
    Serial.print("JSON deserialization failed: ");
    Serial.println(error.c_str());
    return;
  }

  // Access JSON values
  if (doc.containsKey("tp")) {
    std::string com = doc["tp"];

    Serial.print("Received command: ");
    Serial.println(com.c_str());

    std::string start_try = "sta";
    std::string stop_try = "sto";
    std::string off_try = "off";
    // Start experiment and configure parameters
    if (doc["tp"] == start_try && Config::start_exp != 2) {
      Serial.println("message is from sta");
      Config::start_exp = 1;
      Config::tot_time_exp = doc["t"];
      Config::freq_exp = doc["hz"];
      Config::size_packet_exp = doc["ps"];
      Config::qts = doc["qts"];
      Config::calc_time = doc["ct"];
      // write configure in message
      int cur_pos = 0;
      int add_pos;
      int conf_values[5] = {Config::tot_time_exp, Config::freq_exp, Config::size_packet_exp, Config::qts, Config::calc_time};
      // this message will be used to start the broker containing the parameters of the experiment
      for (int i=0; i<5; i++){
        snprintf(&Config::new_message[300], PLUGIN_SZ, "%d", conf_values[i]);
        add_pos = strlen(&Config::new_message[300]);
        if (add_pos < (PLUGIN_SZ - cur_pos)){
          if (cur_pos != 0){
            snprintf(&Config::new_message[cur_pos], PLUGIN_SZ - cur_pos, "_");
            ++cur_pos;
          }
          snprintf(&Config::new_message[cur_pos], PLUGIN_SZ, "%d", conf_values[i]);
          cur_pos += add_pos;
        } 
      }

    } else if (doc["tp"] == stop_try){
      Config::stop_exp = 1;
    } else if (doc["tp"] ==off_try) {
      M5.Axp.PowerOff();
    }

  }
}
