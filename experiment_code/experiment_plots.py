# File with all the plots used in the experiment
# WARNING: INCLUDES NOT USED TESTS

from data_analysis import *
import matplotlib.pyplot as plt
import control_func as cf


# ALL PLOTS USED FOR THE EXPERIMENT
if __name__ == "__main__":
    # EXPERIMENT GATE PROCESSING FIRST PACKET LOSS
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 0)
        client.change_single("hz", 100) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_calctime", "ct", steps=120, limits=[5000,19000], source="paho")

        plt.plot(plot_data[0], plot_data[1], label="Packet loss Gateway client")
        show_5_perc_point(plot_data[0], plot_data[1], "ms")
        i_data = 71
        show_5_perc_point(plot_data[0][i_data:], plot_data[1][i_data:], "ms")
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('time (ms)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying Gateway processing time')
        plt.grid(True)
        plt.legend()
        plt.show()

    # EXPERIMENT GATE PROCESSING SECOND DELAY
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_calctime_2", "ct", steps=100, limits=[1400,4500], source="paho", data_type="delay")

        plt.plot(plot_data[0][40:], [i/1000_000 for i in plot_data[1]][40:])
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('processing time (ms)')
        plt.ylabel('delay (ms)')
        plt.title('Varying Gateway processing time')
        plt.grid(True)
        plt.show()

    # EXPERIMENT GATE PROCESSING SECOND PACKET LOSS
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_calctime_2", "ct", steps=120, limits=[1400,4500], source="paho")

        plt.plot(plot_data[0], plot_data[1], label="Packet loss Gateway client")
        show_5_perc_point(plot_data[0], plot_data[1], "ms")

        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('time (ms)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying Gateway processing time')
        plt.grid(True)
        plt.legend()
        plt.show()

    # EXPERIMENT GATE PROCESSING FIRST DELAY
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 0)
        client.change_single("hz", 100) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_calctime", "ct", steps=120, limits=[5000,19000], source="paho", data_type="delay", full_dir=False)

        plt.plot(plot_data[0], [i/1000_000 for i in plot_data[1]])
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('processing time (ms)')
        plt.ylabel('delay (ms)')
        plt.title('Varying Gateway processing time')
        plt.grid(True)
        plt.show()




    # EXPERIMENT FREQUENCY FIRST
    if (False):
        client = cf.ExperimentClient()
        client.change_single("ps", 337)
        client.change_single("hz", 100) 
        client.change_single("t", 5000)
        client.change_single("ct", 0)

        plot_data = get_data_packet_loss(client, "experiment_frequency_2", "hz", steps=50, limits=[100,5000])
        # da.get_threshold(plot_data[0], plot_data[1], plot_data[2])
        plt.plot(plot_data[0], plot_data[1], label="Loss Unit, Broker, Gateway")
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('frequency (hz)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying frequency')
        plt.legend()
        plt.grid(True)
        plt.show() 

    # EXPERIMENT JITTER FIRST
    if (False):
        client = cf.ExperimentClient()
        client.change_single("ps", 337)
        client.change_single("hz", 100) 
        client.change_single("t", 5000)
        client.change_single("ct", 0)

        plot_data = get_data_packet_loss(client, "experiment_frequency_2", "hz", steps=50, limits=[100,5000],data_type="jitter")
        # da.get_threshold(plot_data[0], plot_data[1], plot_data[2])
        # plt.plot(plot_data[0], plot_data[1])
        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('frequency (hz)')
        plt.ylabel('jitter (ms)')
        plt.title('Varying frequency')
        plt.grid(True)
        plt.show() 



    # PACKET SIZE TEST 1

    if (False):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_size_1", "ps", steps=50, limits=[50,2000])

        # plt.plot(plot_data[0], plot_data[1])
        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label="Loss Unit, Broker, Gateway")
        plt.xlabel('message size (B)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying message size')
        plt.legend
        plt.grid(True)
        plt.show()

    # PACKET SIZE TEST 2
    if (False):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_size_2", "ps", steps=25, limits=[1300,1500])

        plt.plot(plot_data[0], plot_data[1])
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Packets send per hz')
        plt.legend()
        plt.grid(True)
        plt.show()
    

        # PACKET SIZE TEST 2
    if (False):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_size_2", "ps", steps=25, limits=[1300,1500])

        plt.plot(plot_data[0], plot_data[1])
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Packets send per hz')
        plt.legend()
        plt.grid(True)
        plt.show()

    # WiFi packet loss
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 10000)
        client.change_single("ps", 324)

        plot_data = get_data_packet_loss(client, "experiment_wifi_3", "wifi", steps=[-30, -50, -60, -65, -70, -75, -80], limits=[1300,1500])

        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, marker='o', label="wifi strength Unit")
        show_5_perc_point(plot_data[0], plot_data[1], "dB", reverse=True)
        plt.xlabel('WiFi SNR (dB)')
        plt.ylabel('Packet loss')
        plt.title('Varying WiFi')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    # WiFi jitter
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 10000)
        client.change_single("ps", 324)

        plot_data = get_data_packet_loss(client, "experiment_wifi_3", "wifi", [-30, -50, -60, -65, -70, -75], None, full_dir=False, data_type="jitter")

        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, marker='o')
        plt.xlabel('WiFi SNR (dB)')
        plt.ylabel('jitter (s)')
        plt.title('Varying WiFi')
        plt.grid(True)
        plt.show()


    # PACKET SIZE TEST 3
    if (False):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_size_3", "ps", steps=25, limits=[1300,4000], wifi_str=[-50, 0])

        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5)
        plt.xlabel('message size (B)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying message size')
        plt.grid(True)
    #     plt.show()

# =========================================================================== NEW EXPERIMENTS
    # packets
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 10000)

        plot_data = get_data_packet_loss(client, "new_experiment_size_1", "ps", steps=100, limits=[50,2000], wifi_str=[-50, None])
        

        # plt.plot(plot_data[0], plot_data[1])
        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label="Loss Unit, Broker, Gateway", errorevery=(1, 3))
        show_5_perc_point(plot_data[0], plot_data[1], "B")

        plt.xlabel('message size (B)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying message size')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    # if (True):
    #     client = cf.ExperimentClient()
    #     client.change_single("ct", 0)
    #     client.change_single("hz", 400) 
    #     client.change_single("t", 10000)

    #     plot_data = get_data_packet_loss(client, "new_experiment_size_1", "ps", steps=100, limits=[50,2000], wifi_str=[-50, None], data_type="jitter")

    #     # plt.plot(plot_data[0], plot_data[1])
    #     plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label="Loss Unit, Broker, Gateway", errorevery=(1, 3))
    #     plt.xlabel('message size (B)')
    #     plt.ylabel('packet loss (%)')
    #     plt.title('Varying message size')
    #     plt.legend
    #     plt.grid(True)
    #     plt.show()

    if (True):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 10000)

        plot_data = get_data_packet_loss(client, "new_experiment_size_3", "ps", steps=250, limits=[1000,10000], wifi_str=[-50, None])

        # plt.plot(plot_data[0], plot_data[1])
        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label="Loss Unit, Broker, Gateway", errorevery=(1, 6))
        show_5_perc_point(plot_data[0], plot_data[1], "B")
        plt.xlabel('message size (B)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying message size')
        plt.legend()
        plt.grid(True)
        plt.show()
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ct", 0)
        client.change_single("hz", 400) 
        client.change_single("t", 10000)

        plot_data = get_data_packet_loss(client, "new_experiment_size_3", "ps", steps=100, limits=[1000,10000], wifi_str=[-50, None], data_type="jitter")

        # plt.plot(plot_data[0], plot_data[1])
        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label="Loss Unit, Broker, Gateway", errorevery=(1, 6))
        plt.xlabel('message size (B)')
        plt.ylabel('jitter (ms)')
        plt.title('Varying message size')
        plt.grid(True)
        plt.show()
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 337)
        client.change_single("hz", 100) 
        client.change_single("t", 10000)
        client.change_single("ct", 0)

        plot_data = get_data_packet_loss(client, "new_experiment_frequency_1", "hz", steps=100, limits=[100,5000], wifi_str=[-50, None])
        # da.get_threshold(plot_data[0], plot_data[1], plot_data[2])
        plt.plot(plot_data[0], plot_data[1], label="Loss Unit, Broker, Gateway")
        show_5_perc_point(plot_data[0], plot_data[1], "Hz")
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('frequency (Hz)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying frequency')
        plt.legend()
        plt.grid(True)
        plt.show() 

    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 337)
        client.change_single("hz", 100) 
        client.change_single("t", 10000)
        client.change_single("ct", 0)

        plot_data = get_data_packet_loss(client, "new_experiment_frequency_1", "hz", steps=100, limits=[100,5000], wifi_str=[-50, None], data_type="jitter")
        # da.get_threshold(plot_data[0], plot_data[1], plot_data[2])
        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, errorevery=(1, 3))
        plt.xlabel('frequency (Hz)')
        plt.ylabel('jitter (ms)')
        plt.title('Varying frequency')
        plt.grid(True)
        plt.show() 

    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 3487)
        client.change_single("hz", 100) 
        client.change_single("t", 10000)
        client.change_single("ct", 0)

        plot_data = get_data_packet_loss(client, "new_experiment_frequency_2", "hz", steps=100, limits=[100,5000], wifi_str=[-50, None])
        # da.get_threshold(plot_data[0], plot_data[1], plot_data[2])
        plt.plot(plot_data[0][0:50], plot_data[1][0:50], label="Loss Unit, Broker, Gateway")
        show_5_perc_point(plot_data[0], plot_data[1], "Hz")

        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('frequency (Hz)')
        plt.ylabel('packet loss (%)')
        plt.title('Varying frequency')
        plt.legend()
        plt.grid(True)
        plt.show() 

    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 3487)
        client.change_single("hz", 100) 
        client.change_single("t", 10000)
        client.change_single("ct", 0)

        plot_data = get_data_packet_loss(client, "new_experiment_frequency_2", "hz", steps=100, limits=[100,5000], wifi_str=[-50, None], data_type="jitter")
        # da.get_threshold(plot_data[0], plot_data[1], plot_data[2])
        plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, errorevery=(1, 3))
        plt.xlabel('frequency (Hz)')
        plt.ylabel('jitter (ms)')
        plt.title('Varying frequency')
        plt.grid(True)
        plt.show() 

#=========================================================== Discussion calculations
    if (True):
        client = cf.ExperimentClient()
        client.change_single("ps", 0)
        client.change_single("hz", 100) 
        client.change_single("t", 5000)

        plot_data = get_data_packet_loss(client, "experiment_calctime", "ct", steps=120, limits=[5000,19000], source="paho", data_type="delay", full_dir=False)
        plt.plot(plot_data[0], [i/1000_000 for i in plot_data[1]], label="Packet loss Gateway client")
        plot_math_function([10.00, 14], "Estimation", lambda p:plot_data[1][0]/1000_000+(p-1000/100)*100*5)
        # plt.errorbar(plot_data[0], plot_data[1], yerr=plot_data[2], capsize=5, label='Data')
        plt.xlabel('processing time (ms)')
        plt.ylabel('delay (ms)')
        plt.title('Varying Gateway processing time')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    if (True):
        plot_math_function([50, 400], "Estimated 5% packet loss", lambda f: 1.05/f*1000)
        plt.xlabel('frequency (Hz)')
        plt.ylabel('processing time (ms)')        
        plt.legend()
        plt.grid(True)
        plt.show()

#================================================= main Experiment
    show_main_experiment("main2.csv", estimation=True)
    show_main_experiment("main2.csv", data_type="through", estimation=False)

