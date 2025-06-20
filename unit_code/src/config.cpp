#include "config.h"

namespace Config{
    int start_exp = 0;
    int stop_exp = 0;

    // parameters
    // frequency
    int freq_exp = 0;
    // size
    unsigned int size_packet_exp = 0;
    // total time experiment in millisec
    int tot_time_exp = 0;
    //Qts
    int qts = 0;
    // calculate time paho client in microseconds
    int calc_time = 0;
    // message that will be send
    char new_message[10200] = {0};  // Initializes all bytes to 0
    
}