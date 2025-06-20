#pragma once
// used to start and stop the experiment
#define PLUGIN_SZ 200
namespace Config{
    // 0, no experiment, 1 start experiment, 2 experiment is in progress
    extern int start_exp;
    // 0 no, 1 stop experiment
    extern int stop_exp;

    // parameters
    // frequency
    extern int freq_exp;
    // size
    extern unsigned int size_packet_exp;
    // total time experiment in millisec
    extern int tot_time_exp;
    //Qts
    extern int qts;
    // calculate time on paho client in microseconds
    extern int calc_time;
    // new message buffer
    extern char new_message[10200];

}
