import matplotlib.pyplot as plt
import control_func as cf
import copy
import file_names_exp as fn
import pandas as pd
import numpy as np
import spline_analysis as da
import os


# returns the mean and std of the panday array jitter
def pandas_get_jitter_single(panda_array):
    panda_new = (panda_array.iloc[:, 1]/1000)/panda_array.iloc[:, 0]
    return panda_new.mean(), panda_new.std()

# return the mean and std of the packet loss in percentage
def pandas_get_packet_loss_single(panda_array, client_file_name, source="unit"):
    match source:
        case "unit":
            j = 0
        case "broker":
            j = 2
        case "paho":
            j = 3

    panda_array.replace(-1, 0)
    act_data =panda_array.iloc[:, j]
    file_name_split = [int(i) for i in client_file_name.split("_")]
    act_data = (act_data/(file_name_split[0]*file_name_split[1]))*100_000
    return max(0,100-act_data.mean()), act_data.std()

# get throughput in kB
def pandas_get_throughput_single(panda_array, client_file_name, source="unit"):
    match source:
        case "unit":
            j = 0
        case "broker":
            j = 2
        case "paho":
            j = 3
    panda_array.replace(-1, 0)
    act_data = panda_array[j]
    file_name_split = [int(i) for i in client_file_name.split("_")]
    return  file_name_split[2]*act_data.mean()/((file_name_split[0]/1000)*1000)


# get the delay (in )
def pandas_get_delay_single(panda_array):
    panda_new = panda_array.iloc[:,4]
    panda_new = panda_new[panda_new != -1]
    return panda_new.mean(), panda_new.std()


# get the message size from payload size
def get_true_size(client_file_name):
    file_name_split = [int(i) for i in client_file_name.split()]
    if file_name_split[2] > 255:
        return file_name_split[2]+12
    else:
        return file_name_split[2]+11

# get SNR from RSSI and noise floor
def constant_noise(panda_array, noise_floor):
    return panda_array[:, 5] - noise_floor

# helper function used with full dir parameter
def get_all_steps(name, dir_name):
    steps = []
    match name:
        case "hz":
            index = 1
        case "ps":
            index = 2
        case "ct":
            index = 4
        case "wifi":
            index = 6
    for file_name in os.listdir(dir_name):
        file_name = file_name.split(".")[0]
        steps.append(int(file_name.split("_")[index]))
    return steps

# get data, packet_loss, jitter, delay, throughput
# dir = directory of data, name = name of the varying variable, steps= steps of the var variable, limits= limits between the steps
# source= source of packet loss data, data_type = type of data jitter-packet loss etc., wifi_str = [mean, std], full_dir= use all data from data dir overriding steps
def get_data_packet_loss(client: cf.ExperimentClient, dir, name, steps, limits, units = 1, source="unit", data_type="packet",  wifi_str: list = [None, None], full_dir=True):
    if type(steps) != list:
        try:
            steps = [int(limits[0]+(limits[1]-limits[0])*(i/(steps-1))) for i in range(steps)]
        except:
            raise ValueError("limits needs to be a list with len 2")
    
    #to not mutate the default list
    if wifi_str == [None, None]:
        wifi_str = [None, None]

    data_dir = f"{fn.actual_data_dir}/{dir}"
    if full_dir:
        steps = get_all_steps(name, data_dir)
        steps.sort()
    
    new_steps = []
    mean_data = []
    std_data = []
    # retrieve relevant data
    for step in steps:
        new_conf = client.get_config()
        if (name !="wifi"):
            new_conf[name] = step
        else:
            wifi_str[0]=step



        file_name = f"{client.file_name_con(new_conf, am_units=units, wifi=wifi_str[0])}"
        try:
            df = pd.read_csv(f"{data_dir}/{file_name}", header=None)
        except:
            continue
    # calculation
        match data_type:
            case "packet":
                new_mean, new_std = pandas_get_packet_loss_single(df, file_name.split(".")[0], source=source)
            case "jitter":
                new_mean, new_std = pandas_get_jitter_single(df)
            case "delay":
                new_mean, new_std = pandas_get_delay_single(df)
            case "through_put":
                new_mean, new_std = pandas_get_throughput_single(df, file_name.split(".")[0], source=source)
                
        
        mean_data.append(new_mean)
        std_data.append(new_std)
        if name=="wifi":
            new_steps.append(step+95)
        elif name=="ct":
            new_steps.append(step/1000)
        else:
            new_steps.append(step)
    
    return new_steps, mean_data, std_data

# used for estimation in experiment with message size in relation to the message frequency and 5% threshold
def plot_estimation_big_experiment(throughput=False):
    y = 650
    x_list = [0]
    y_list = [650]
    through = [0]
    change = 0.987
    for i in range(1, 150):
        x_list.append(i*(7500/150))
        y = y*change
        y_list.append(y)
        through.append(y*i*(7500/150)/1000)

    if (throughput):
        plt.plot(x_list, through, label=f"model")
    else:
        plt.plot(x_list, y_list, label=f"model")

# show the experimentent with message size in relation to the message frequency and 5% threshold
def show_main_experiment(file_name, data_type="packet", estimation=False):
    df = pd.read_csv(f"{fn.processed_dir}/{file_name}", header=None)
    if data_type == "packet":
        plt.errorbar(df[0].to_numpy(), df[1].to_numpy(), yerr=[df[2].to_numpy(), df[3].to_numpy()], marker='o', markersize=2, capsize=5, label="real experiment")
        if estimation:
            plot_estimation_big_experiment()
        plt.grid(True)
        plt.xlabel('message size (B)')
        plt.ylabel('frequency (Hz)')
        if estimation:
            plt.legend()
        plt.title("5% packet loss")
    elif data_type == "through":
        plt.plot(df[0].to_numpy(), df[4].to_numpy()/1000, marker='o', markersize=2, label="real experiment")
        if estimation:
            plot_estimation_big_experiment(throughput=True)
        plt.grid(True)
        plt.xlabel('message size (B)')
        plt.ylabel('throughput KB/s')
        if estimation:
            plt.legend()
        plt.title("5% packet loss")


    plt.show()

# plot a user defined math function
def plot_math_function(limits, label, function, steps=100):
    x = np.linspace(limits[0], limits[1], num=steps)
    y = function(x)
    plt.plot(x, y, label=label)


# plots the 5% point in experiments in red (unit= the unit in which the measurements took place)
def show_5_perc_point(plot_x, plot_y, unit, show_dot=True, reverse=False):
    tresh = None
    for i in range(len(plot_y)):
        if reverse and plot_y[i] < 5:
            tresh = i
            break
        elif not reverse and (plot_y[i]) > 5:
            tresh = i
            break
    try:
        if 1 <= tresh < len(plot_y):
            print(plot_x[i-1:i+1], plot_y[i-1:i+1])
            plt.plot(plot_x[i-1:i+1], plot_y[i-1:i+1], 'r-', zorder=10, label=f"5% threshold ({plot_x[i-1]} {unit}, {plot_x[i]} {unit})")
            if (show_dot):
                plt.scatter(plot_x[i-1:i+1], plot_y[i-1:i+1], color='red', s=20)
    except:
        raise RuntimeError("no threshold found")
            


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

