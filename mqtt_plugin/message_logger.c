// Mosquitto plugin made to collect data from the Unit, Gateway and Broker
// QoS is mentioned but not in use (does not work)
// print (LOG) statements only work if you dont run it via systemd
// IMPORTANT FOR MOSQUITTO TO HAVE PERMISSION TO -> /mosquitto_data

#define _GNU_SOURCE // otherwise strdup not recognized
#define _POSIX_C_SOURCE 199309L  // Enable POSIX features (for clock_gettime)
#include <mosquitto_broker.h>
#include <mosquitto_plugin.h>
#include <mosquitto.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <inttypes.h>
#include <unistd.h>

#define SIZE_CONF 200
static mosquitto_plugin_id_t *plugin_id;
// Experiment configurations
char exp_configure [SIZE_CONF] = {};
// Packets unit send
int real_amount_packets = 0;
// Jitter sum from Units
int jitter_sum = 0;
// Packets the broker received
int amount_packets = 0;
// Packets the Gateway client received
int paho_packets = 0;
// Gateway state identifier
int experiment_current;

// control messages to the Gateway client
char *paho_start = "exp/paho_start";
char *paho_stop = "exp/paho_stop";
// data path measurements
char *data_dir = "/var/lib/mosquitto/mosquitto_data";

// AMOUNT UNITS CONTROL
// used to determine if gather time passed
double start_time_gather;
#define GATHER_TIME 0.01
// active units in the current experiment
int active_units = 0;
// total units that were active in the experiment
int total_units;
// nano second time precision
struct timespec start_time_paho, stop_time_paho;
// used to store the interval between start_time_paho and stop_time_paho
long total_time_paho;

// Different possible messages
typedef enum {
    TOP_START_EXP,
    TOP_STOP_EXP,
    TOP_STOP_ABP,
    TOP_RUN,
    TOP_STOP_FROM_PAHO,
    TOP_CHECK,
    TOP_INV
} Topic_packet;

// Translate to enum
Topic_packet get_packet_type(const char* topic) {
    if (strcmp(topic, "cur/cur") == 0) return TOP_RUN;
    if (strcmp(topic, "exp/plug_stop") == 0) return TOP_STOP_EXP;
    if (strcmp(topic, "exp/stop") == 0) return TOP_STOP_ABP;
    if (strcmp(topic, "exp/plug_start") == 0) return TOP_START_EXP;
    if (strcmp(topic, "exp/paho_send_stop") == 0) return TOP_STOP_FROM_PAHO;
    if (strcmp(topic, "exp/check") == 0) return TOP_CHECK;
    // Topic invalid
    return TOP_INV;
}

// Structure to hold broker messages which contain one 64 bit integer
typedef struct {
    char *topic;
    int64_t value;
    int qos;
    bool retain;
} broker_message;

// used to send to messages from the broker to the paho client
static void publish_broker_message(void *userdata)
{
    broker_message *data = (broker_message *)userdata;
    
    // Convert 64-bit integer to string
    char payload[21]; // Enough for 64-bit decimal + null terminator
    snprintf(payload, sizeof(payload), "%ld", data->value);
    
    // Publish the message
    mosquitto_broker_publish_copy(
        NULL,
        data->topic,
        strlen(payload),
        payload,
        data->qos,
        data->retain,
        NULL
    );
    
    // Clean up
    free(data->topic);
    free(data);
}


static void send_start_paho_message(){
    broker_message *data = malloc(sizeof(broker_message));
    if (!data) exit(1);
    

    // find start of processing time integer in string for Gateway client
    int amount_underscore = 0;
    int start_index_calc_time;
    for(int i = 0; i < strlen(exp_configure); i++){
        if (exp_configure[i] == '_'){
            amount_underscore += 1;
        } else{
            if (amount_underscore == 4){
                start_index_calc_time = i;
                break;
            }
        }
    }
    // define message structure
    data->topic = strdup(paho_start);
    data->value = atoi(&exp_configure[start_index_calc_time]); // payload containing processing time
    data->qos = 1;
    data->retain = false;
    publish_broker_message((void *) data);
}

static void send_stop_paho_message(){
            // Create delayed message data
    broker_message *data = malloc(sizeof(broker_message));
    if (!data) exit(1);
    
    data->topic = strdup(paho_stop);
    data->value = 0; // no payload
    data->qos = 1;
    data->retain = false;
    publish_broker_message((void *) data);

}
// Write the result of an experiment
int write_result(){
    FILE *file;
    char file_name[250];
    snprintf(file_name, 250, "%s/%s_%d.txt", data_dir, exp_configure, total_units);
    
    file = fopen(file_name, "a");

    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }
    
    // Append text to the file
    if (fprintf(file, "%d, %d, %d, %d, %ld\n", amount_packets, jitter_sum, real_amount_packets, paho_packets, total_time_paho) < 0) {
        perror("Error writing to file");
        fclose(file);
        return 1;
    }
    printf("%d, %d, %d, %d, %ld written\n", amount_packets, jitter_sum, real_amount_packets, paho_packets, total_time_paho);
    // Close the file
    if (fclose(file) != 0) {
        perror("Error closing file");
        return 1;
    }

}
// three states
// 0 waiting for experiment to start
// 1 experiment started, more units could arive
// 2 experiment fully started more units denied
// 3 experiment stopped waiting for paho client
int on_message(int event, void *event_data, void *userdata)
{
    struct mosquitto_evt_message *msg = (struct mosquitto_evt_message *)event_data;

    if (msg && msg->topic){
        Topic_packet cur_pack = get_packet_type(msg->topic);
        if (experiment_current){
            // gather time stage (used to gather Units which are still activating), experiment already started
            if (experiment_current == 1){
                if (cur_pack == TOP_RUN) {
                    amount_packets += 1;
                } 
                // check if in gather time
                if ((clock()-start_time_gather)/CLOCKS_PER_SEC > GATHER_TIME){
                    experiment_current = 2;
                } else {
                    if (cur_pack == TOP_START_EXP) {
                        active_units += 1;
                        total_units +=1;
                    }
                }
            } else if (experiment_current == 2){
                if (cur_pack == TOP_RUN) {
                    amount_packets += 1;
                
                // abrupt stop, reset plugin
                } else if (cur_pack == TOP_STOP_ABP) {
                    experiment_current = 0;
                    amount_packets = 0;
                    real_amount_packets = 0;
                    jitter_sum = 0;
                    active_units = 0;
                    total_units = 0;
                // stop the experiment normally
                } else if (cur_pack == TOP_STOP_EXP) {
                    // printf("stop experiment received\n");
                    active_units -= 1;
                    int num1, num2;
                    sscanf((const char*)msg->payload, "%d,%d", &num1, &num2);
                    real_amount_packets += num1;
                    jitter_sum += num2;
                    if  (active_units == 0) {
                        experiment_current = 3;
                        clock_gettime(CLOCK_MONOTONIC, &start_time_paho);
                        send_stop_paho_message();
                        // printf("stop message send\n");
                    }
                }
            // experiment already ended but waiting for data from the Gateway client
            } else if (experiment_current == 3){

                if (cur_pack == TOP_STOP_FROM_PAHO){
                    // gateway client delay in nano seconds
                    clock_gettime(CLOCK_MONOTONIC, &stop_time_paho);
                    total_time_paho = (stop_time_paho.tv_sec-start_time_paho.tv_sec)*1000000000+(stop_time_paho.tv_nsec-start_time_paho.tv_nsec);
                    
                    paho_packets = atoi((const char*)msg->payload);
                    printf("stop experiment with %d send packets. %d received broker packets and %d paho packets and %d units\n", real_amount_packets, amount_packets, paho_packets, total_units);
                    
                    if (write_result()){
                        printf("failed file\n");
                        exit(1);
                    };
                    // reset
                    amount_packets = 0;
                    real_amount_packets = 0;
                    jitter_sum = 0;
                    paho_packets = 0;
                    total_units = 0;
                    experiment_current = 0;
                // check message from controller if Gateway client does not react
                } else if (cur_pack == TOP_CHECK){
                    paho_packets = -1;
                    total_time_paho = -1;
                    printf("stop experiment with %d send packets. %d received broker packets and %d paho packets\n", real_amount_packets, amount_packets, paho_packets);
                    if (write_result()){
                        printf("failed file\n");
                        exit(1);
                    };
                    // reset
                    amount_packets = 0;
                    real_amount_packets = 0;
                    jitter_sum = 0;
                    paho_packets = 0;
                    total_units = 0;
                    experiment_current = 0;
                }
            }

        } else {
            // start experiment
            if (cur_pack == TOP_START_EXP){

                experiment_current = 1;
                // safe the configuration in a string
                strncpy(exp_configure, (const char*) msg->payload, SIZE_CONF);
                printf("configuration = %s\n", exp_configure);
                exp_configure[SIZE_CONF - 1] = '\0'; 
                send_start_paho_message();
                
                active_units += 1;
                total_units += 1;
                // gather time if more units will participate
                start_time_gather = clock();

                printf("start experiment\n");
            }
        }
    }

    return MOSQ_ERR_SUCCESS;
}

// OVERLOADED FUNCTIONS
//============================================================================
int mosquitto_plugin_version(int supported_version_count, const int *supported_versions)
{
    printf("mosquitto plugin initialized\n");
    return 5;
}

int mosquitto_plugin_init(mosquitto_plugin_id_t *identifier, void **userdata,
                          struct mosquitto_opt *options, int option_count)
{
    plugin_id = identifier;

    printf("mosquitto plugin registered\n");

    mosquitto_callback_register(
        plugin_id,
        MOSQ_EVT_MESSAGE,
        on_message,
        NULL,
        NULL
    );

    return MOSQ_ERR_SUCCESS;
}

int mosquitto_plugin_cleanup(void *userdata,
                             struct mosquitto_opt *options,
                             int option_count)
{
    mosquitto_log_printf(MOSQ_LOG_INFO, "[PLUGIN] Plugin cleaned up");
    return MOSQ_ERR_SUCCESS;
}
