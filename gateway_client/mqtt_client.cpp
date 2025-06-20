// This file contains code for the MQTT Gateway client
// The main function of this client is too measure the amount of incoming packets
// and simulate processing time through a busy wait

#include <iostream>
#include <cstdlib>
#include <string>
#include <cstring>
#include <cctype>
#include <thread>
#include <chrono>
#include "mqtt/async_client.h"

std::thread publish_thread;

const std::string SERVER_ADDRESS("tcp://localhost:1883");
const std::string CLIENT_ID("paho_cpp_test");
// messages from broker
const std::string TOPIC_START("exp/paho_start");
const std::string TOPIC_STOP("exp/paho_stop");
const std::string TOPIC_RUN("cur/cur");
const std::string TOPIC_ABRP_STOP("exp/stop");
// messages to broker
const std::string TOPIC_SEND("exp/paho_send_stop");

// is client in experiment
int in_experiment = 0;
// delay of messages in experiment
int delay_run_messages = 0;
// measured amount of packets
int amount_packets = 0;

const int QOS = 1;



class callback : public virtual mqtt::callback {
    mqtt::async_client& client;  // Reference to the client
public:
    callback(mqtt::async_client& cli) : client(cli) {}

    void connection_lost(const std::string& cause) override {
        std::cout << "\nConnection lost" << std::endl;
        if (!cause.empty())
            std::cout << "\tcause: " << cause << std::endl;
    }

    void message_arrived(mqtt::const_message_ptr msg) override {
        auto start = std::chrono::steady_clock::now();
        // user stop experiment
        if (msg->get_topic() == TOPIC_ABRP_STOP){
            printf("abrupt stop\n");
            in_experiment = 0;
        }
        // start experiment
        if (msg->get_topic() == TOPIC_START && in_experiment == 0){
            in_experiment = 1;
            amount_packets = 0;
            delay_run_messages = std::stoi(msg->to_string());


        } else if (in_experiment == 1){
            // measure amount of packets
            if (msg->get_topic() == TOPIC_RUN){
                amount_packets += 1;
                // simulate process time
                while (true){
                    auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - start);
                    if (elapsed.count() > delay_run_messages){
                        return;
                    }
                }
            // stop experiment and send a message back to the broker
            } else if (msg->get_topic() == TOPIC_STOP){
                // return amount of packets
                in_experiment = 0;
                auto msg = mqtt::make_message(TOPIC_SEND, std::to_string(amount_packets));
                msg->set_qos(QOS);
                publish_thread = std::thread([this, msg]() {
                    client.publish(msg)->wait();
                });
                publish_thread.detach();

            }
        }

    }

    void delivery_complete(mqtt::delivery_token_ptr token) override {

    }
};

int main(int argc, char* argv[]) {
    // std::cout << "starting flubbers.." << std::endl;
    mqtt::async_client client(SERVER_ADDRESS, CLIENT_ID);
    // std::cout << "starting flubbers.." << std::endl;

    
    // Pass client to callback constructor
    callback cb(client);
    client.set_callback(cb);

    mqtt::connect_options connOpts;
    connOpts.set_keep_alive_interval(20);
    connOpts.set_clean_session(true);

    try {
        std::cout << "Connecting to server '" << SERVER_ADDRESS << "'..." << std::flush;
        client.connect(connOpts)->wait();
        std::cout << "OK" << std::endl;

        // Subscribe to relevant topics
        client.subscribe(TOPIC_START, QOS)->wait();
        client.subscribe(TOPIC_RUN, QOS)->wait();
        client.subscribe(TOPIC_STOP, QOS)->wait();
        client.subscribe(TOPIC_ABRP_STOP, QOS)->wait();

        std::cout << "OK" << std::endl;


        // Wait for messages
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        // Disconnect
        std::cout << "Disconnecting..." << std::flush;
        client.disconnect()->wait();
        std::cout << "OK" << std::endl;
    }
    catch (const mqtt::exception& exc) {
        std::cerr << exc.what() << std::endl;
        return 1;
    }

    return 0;
}