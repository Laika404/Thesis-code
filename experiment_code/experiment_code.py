# File with the main code of the experiments
# If this file causes file perimission errors run program in sudo
import subprocess
import re
import control_func as c
import time
from datetime import datetime
import os
import signal
import pandas as pd
import data_analysis as vis
import spline_analysis as da
import file_names_exp as fe

# used for orphaned Gateway client processes
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

# get average client wifi (WARNING: if more units are used, uses the average between)
def average_client_hotspot():
    interface = "wlo1"
    try:
        # Captures output of all the wifi clients connected to the hotspot
        cmd = f"sudo iw dev {interface} station dump"
        output = subprocess.check_output(cmd, shell=True, text=True)
        
        # Extract all 'signals of units' 
        rssi_values = re.findall(r"signal avg:\s*(-\d+)", output)
        
        if not rssi_values:
            print("No clients connected or 'signal avg' not found.")
            exit(1)
        
        # get average RSSI
        rssi_values = [int(rssi) for rssi in rssi_values]
        avg_rssi = sum(rssi_values) / len(rssi_values)
        
        return avg_rssi
    
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    exit(1)

# used for debugging to find RSSI sweet spots
def hotspot_continious():
    while True:
        print(average_client_hotspot())
        time.sleep(0.5)
# copy all files
def file_copy():
    for file in os.listdir(fe.original_data_dir):
        line = ""
        with open(f"{fe.original_data_dir}/{file}", 'r') as f:
            line = f.readline().strip('\n')
        
        with open(f"{fe.actual_data_dir}/{file}", 'a') as f:
            f.writelines([line+","+str(average_client_hotspot())])

        os.remove(f"{fe.original_data_dir}/{file}")    

# A single experiment
def run_once(client: c.ExperimentClient, repeat=1, check_time=2, dir_name = '', wait_for_wifi=0, wifi_str: tuple = (None, None), 
             message_size = None, duration = None, frequency = None, calc_time = None):
    # change the client configuration
    if duration != None:
        client.change_single("t", int(duration*1000))
    if message_size != None:
        payload_size = max(0, message_size-12)
        if (payload_size >= 257):
            payload_size -= 1
        client.change_single("ps", payload_size)
    if frequency != None:
        client.change_single("hz", frequency)
    if calc_time != None:
        client.change_single("ct", calc_time)

    print(f"new run once with {client.get_config()}")
    
    # remove old data in mosquitto data file
    os.system(f"sudo rm /{fe.original_data_dir}/* > /dev/null")
    
    # make the data path for the data
    if dir_name != '':
        data_path = f"{fe.actual_data_dir}/{dir_name}/"
    else:
        data_path = f"{fe.actual_data_dir}/"
    # make the data
    if os.path.exists(data_path) is False:
        os.mkdir(f"{fe.actual_data_dir}/{dir_name}")

    cur_repeat = 0
    while cur_repeat < repeat:
        for i in range(wait_for_wifi):
            print(average_client_hotspot())
            time.sleep(1)
        # start paho client
        paho_client = subprocess.Popen(["./mqtt_client"])
        time.sleep(0.5)

        client.send_start()
        # sleep for check_time seconds more to let the program stop first
        remain_time = client.get_config()["t"]/1000+check_time
        client_strength = []
        while remain_time > 0:
            client_strength.append(average_client_hotspot())
            remain_time -= 1
            time.sleep(1)
        
        client_wifi_mean = sum(client_strength)/len(client_strength)
        client_wifi_std = sum([(measure-client_wifi_mean)**2 for measure in client_strength])/len(client_strength)

        # terminate the Gateway client
        already_terminated = False
        while True:
            client.send_check()
            time.sleep(0.1)
            if (os.listdir(fe.original_data_dir) != []):
                paho_client.terminate()
                break
            print("broker not responding")
            time.sleep(1)
            if (already_terminated is False):
                paho_client.terminate()
                already_terminated = True
        
        # check if measured wifi is valid
        if (wifi_str[0] != None and wifi_str[1] != None):
            if (client_wifi_mean+client_wifi_std) > (wifi_str[0]+wifi_str[1]):
                print("invalid measurement wifi to big {} > {}".format( (client_wifi_mean+client_wifi_std), (wifi_str[0]+wifi_str[1])))
                continue
            if (client_wifi_mean-client_wifi_std) < (wifi_str[0]-wifi_str[1]):
                print("invalid measurement wifi to small {} < {}".format((client_wifi_mean-client_wifi_std), (wifi_str[0]-wifi_str[1])))
                continue
        # copy data, wifi_str is optional in file name
        for file in os.listdir(fe.original_data_dir):
            if (wifi_str[0] != None):
                file_name_write = f"{data_path}{file.split(".")[0]}_{wifi_str[0]}.csv"
            else:
                file_name_write = f"{data_path}{file.split(".")[0]}.csv"
    
            line = ""
            with open(f"{fe.original_data_dir}/{file}", 'r') as f:
                line = f.readline().strip('\n')
            new_char = ""
            if os.path.exists(file_name_write):
                new_char ="\n"
            with open(file_name_write, 'a') as f:
                f.writelines([new_char+line+","+str(client_wifi_mean)+","+str(client_wifi_std)])
            
            with open(f"{fe.log_file}", 'a') as f:
                f.write(f"AT: {datetime.now().strftime("Day %d, %H:%M:%S")}, CONFIG: {client.get_config()}\n")
                f.write(f"measurement: {line+","+str(client_wifi_mean)+","+str(client_wifi_std)}\n")

            os.remove(f"{fe.original_data_dir}/{file}")
        cur_repeat += 1
        print(f" measurement {cur_repeat} done of {repeat} for client with config{client.get_config()}")
          

# run an experiment in which one variable is varied
def run_bunch(client: c.ExperimentClient, name, steps, limits = None, repeat=1, dir_name = '', check_time=2, wait_for_wifi=0, wifi_str: tuple = (None, None),
              message_size = None, duration = None, frequency = None, calc_time = None, preamble_time=5):
    # variables for printing
    steps_print = len(steps) if type(steps) == list else steps
    duration_print = duration if duration != None else client.get_config()["t"]/1000

    print("this test will take minimumly {} seconds".format( steps_print*repeat*(check_time+duration_print+wait_for_wifi+0.6)))
    for i in range(preamble_time):
        print(f"starting in {5-i}")
        time.sleep(1)
    # to know how long the experimetn took
    start_time = time.time()

    if type(steps) != list:
        try:
            steps = [int(limits[0]+(limits[1]-limits[0])*(i/(steps-1))) for i in range(steps)]
        except:
            raise ValueError("limits needs to be a tuple")

    for step in steps:
        print(step)
        if name != "wifi":
            client.change_single(name, step)
            print(client.get_config())
            run_once(client, repeat=repeat, dir_name=dir_name, check_time=check_time, wait_for_wifi=wait_for_wifi, wifi_str=wifi_str,
                 message_size=message_size, duration=duration, frequency=frequency, calc_time=calc_time)
        else:
            run_once(client, repeat=repeat, dir_name=dir_name, check_time=check_time, wait_for_wifi=wait_for_wifi, wifi_str=[step, wifi_str[1]],
                 message_size=message_size, duration=duration, frequency=frequency, calc_time=calc_time)
    
    print("The experiment took {} while it was expected to take {}".format(time.time()-start_time,  steps_print*repeat*(check_time+duration_print+wait_for_wifi+0.6)))

# finds a packet loss percentage point through a binary search
def find_point(client:c.ExperimentClient, percentage,  wifi_str: tuple = (None, None), duration=2):
    # duration is always 15
    direction = 1
    cur_hz = 30
    run_hz = 500
    old_loss = 0

    find_point_dir =  "./experiment_data/junk_measure/"

    os.system(f"sudo trash-put {find_point_dir}*")
    run_once(client, duration=duration, frequency=cur_hz, dir_name="junk_measure", repeat=2, wifi_str=wifi_str)
    df = pd.read_csv(f"{find_point_dir}{client.file_name_con(wifi=wifi_str[0])}", header=None)
    old_loss = vis.pandas_get_packet_loss_single(df, client.file_name_con(wifi=wifi_str[0]).split(".")[0])[0]
    
    while True:
        os.system(f"sudo trash-put {find_point_dir}*")
        run_once(client, duration=3, frequency=cur_hz, dir_name="junk_measure", repeat=2, wifi_str=wifi_str)
        df = pd.read_csv(f"{find_point_dir}{client.file_name_con(wifi=wifi_str[0])}", header=None)
        new_loss = vis.pandas_get_packet_loss_single(df, client.file_name_con(wifi=wifi_str[0]).split(".")[0])[0]
        
        print("for {} hz, {}% loss".format(cur_hz, new_loss))
        
        if (new_loss >= percentage):
            direction = -1
            if old_loss < percentage and new_loss > percentage:
                run_hz = run_hz // 2
        else:
            direction = 1
            if old_loss > percentage and new_loss < percentage:
                run_hz = run_hz // 2
        print(f"new hz will be {cur_hz} + {run_hz} * {direction}")
        if (run_hz <=5):
            break
        cur_hz = max(1, cur_hz+ run_hz * direction)
    return cur_hz


# run an experiment with message size and frequency
def run_main_experiment(client: c.ExperimentClient, steps_approx, steps_size, file_name="main.csv", 
                        limits_size = None, repeat=1, dir_name = 'notadir', check_time=2, wait_for_wifi=0, wifi_str: tuple = (None, None),
                         duration = None, calc_time = None, preamble_time = 5):


    steps_size_print = len(steps_size) if type(steps_size) == list else steps_size
    duration_print = duration if duration != None else client.get_config()["t"]/1000

    print("this test will take minimumly {} seconds".format( steps_size_print*steps_approx*repeat*(check_time+duration_print+wait_for_wifi+0.6)))
    for i in range(preamble_time):
        print(f"starting in {5-i}")
        time.sleep(1)

    data_path = f"{fe.actual_data_dir}/{dir_name}/"
    if os.path.exists(data_path) is False:
        os.mkdir(f"{fe.actual_data_dir}/{dir_name}")
    
    if duration != None:
        client.change_single("t", int(duration*1000))
    if calc_time != None:
        client.change_single("ct", calc_time)

    if type(steps_size) != list:
        try:
            steps_size = [int(limits_size[0]+(limits_size[1]-limits_size[0])*(i/(steps_size-1))) for i in range(steps_size)]
        except:
            raise ValueError("limits needs to be a tuple")

    for step_s in steps_size:
        client.change_single("ps", step_s)

        find_duration = 3
        while True:
            loss_2 = find_point(client, 2, wifi_str=wifi_str, duration=find_duration)
            loss_12 = find_point(client, 12, wifi_str=wifi_str, duration=find_duration)
            print(f"FOUND VALUES 2%={loss_2} & 12%={loss_12}")
            
            run_bunch(client, "hz", steps_approx, limits=[loss_2, loss_12], duration=duration, calc_time=calc_time, dir_name=f"{dir_name}/data_ps_{step_s}",
                    wait_for_wifi=wait_for_wifi, wifi_str=wifi_str, repeat=repeat, check_time=check_time, preamble_time=0)

            #  find point of 5%
            full_data = vis.get_data_packet_loss(client, f"{dir_name}/data_ps_{step_s}", "hz", steps_approx, limits=[loss_2, loss_12], wifi_str=wifi_str)
            if (da.get_threshold(*full_data, 5)[0] != -1):
                break
            # experiment failed 5% could not be find, try again
            find_duration = int(find_duration*1.5)
            os.system(f"sudo trash-put {fe.actual_data_dir}/{dir_name}/data_ps_{step_s}/*")



# organizes the data from the message size, message frequency experiment so that it can be used for plotting
def organize_main_experiment_data(client: c.ExperimentClient, steps_approx, steps_size, file_name="main", 
                        limits_size = None, dir_name = 'notadir', wifi_str: tuple = (None, None),
                        calc_time = None, duration=None, show_graph=False):
    # file for new data
    file_name = f"{file_name}.csv"
    data_path = f"{fe.actual_data_dir}/{dir_name}/"
    if os.path.exists(data_path) is False:
        os.mkdir(f"{fe.actual_data_dir}/{dir_name}")
    
    if duration != None:
        client.change_single("t", int(duration*1000))
    if calc_time != None:
        client.change_single("ct", calc_time)

    if type(steps_size) != list:
        try:
            steps_size = [int(limits_size[0]+(limits_size[1]-limits_size[0])*(i/(steps_size-1))) for i in range(steps_size)]
        except:
            raise ValueError("limits needs to be a list with len = 2")
    
    # perform the threshold algorithm splines on all data
    for step_s in steps_size:
        client.change_single("ps", step_s)
        full_data_loss = vis.get_data_packet_loss(client, f"{dir_name}/data_ps_{step_s}", "hz", steps_approx, limits=[0, 0], wifi_str=wifi_str)
        freq_s = da.get_threshold(*full_data_loss, 5, show=show_graph)
        with open(f"{fe.processed_dir}/{file_name}", 'a') as file:
            file.write(f"{step_s},{freq_s[0]},{freq_s[1][0]}, {freq_s[1][1]}, {max(0, freq_s[0]*step_s*0.95)}\n")
