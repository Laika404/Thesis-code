# The code to run all the experiments in  the thesis
# WARNING SOME EXPERIMENTS ARE NOT USED IN THESIS
# IF FILE PERMISSION ERRORS, RUN IN SUDO

import control_func as c
from auto_exp import *

# processing 1 
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ct", steps= 120, limits=[5000, 19000], 
              repeat=5, dir_name="experiment_calctime", wifi_str=[-35, 2], message_size=0, duration=5, frequency=100)


# processing 2
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ct", steps= 100, limits=[1000, 4500], 
              repeat=5, dir_name="experiment_calctime_2", wifi_str=[-35, 2], message_size=0, duration=5, frequency=400)


# test processing time
if __name__ == "__main__":

    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "hz", steps= 20, limits=[400, 2500], 
              repeat=5, dir_name="haha", wait_for_wifi=2, wifi_str=[-35, 2.5], calc_time=0, message_size=180, duration=5)
    

# frequency 1
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "hz", steps= 50, limits=[100, 5000], 
              repeat=5, dir_name="experiment_frequency_1", wifi_str=[-50, 2], message_size=350, duration=5, calc_time=0)
    

# packet size test 1
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ps", steps= 50, limits=[50, 2000], 
              repeat=5, dir_name="experiment_size_1", wifi_str=[-50, 2], frequency=400, duration=5, calc_time=0)
    

# packet size test 2
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ps", steps= 25, limits=[1300, 1500], 
              repeat=5, dir_name="experiment_size_2", wifi_str=[-50, 2], frequency=400, duration=5, calc_time=0)
    
# MAIN EXPERIMENT

    # run_bunch(main_client, "wifi", steps= 8, limits=[-35, -75], 
    #           repeat=4, dir_name="experiment_wifi_1", wifi_str=[-69, 2], frequency=400, duration=4, calc_time=0)
    run_main_experiment(main_client, 20, 15, limits_size=[0, 4000], duration=10, repeat=3, wifi_str=[-50, 2], dir_name="main_experiment2")
    organize_main_experiment_data(main_client, 20, 15, limits_size=[0, 4000], duration=10, wifi_str=[-50, 2], dir_name="main_experiment2")


# packet size tesst 2
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ps", steps= 50, limits=[1000, 4000], 
              repeat=5, dir_name="experiment_size_3", wifi_str=[-50, 2], frequency=400, duration=5, calc_time=0)
    


# wifi test 1
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()

    run_bunch(main_client, "wifi", steps= [-30, -50, -60, -65, -70, -75, -80], 
              repeat=5, dir_name="experiment_wifi_3", wifi_str=[-69, 2], frequency=400, duration=10, calc_time=0, message_size=337)
    


# NEW LONGER TESTS

# packet size test 1
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ps", steps= 100, limits=[50, 2000], 
              repeat=6, dir_name="new_experiment_size_1", wifi_str=[-50, 2], frequency=400, duration=10, calc_time=0)


# packet size tesst 2
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ps", steps= 100, limits=[1000, 4000], 
              repeat=6, dir_name="new_experiment_size_2", wifi_str=[-50, 2], frequency=400, duration=10, calc_time=0)
    
# frequency test 1

# frequency 1
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "hz", steps= 100, limits=[100, 5000], 
              repeat=6, dir_name="new_experiment_frequency_1", wifi_str=[-50, 2], message_size=350, duration=10, calc_time=0)

# frequency test 2
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "hz", steps= 100, limits=[100, 5000], 
              repeat=6, dir_name="new_experiment_frequency_2", wifi_str=[-50, 2], message_size=3500, duration=10, calc_time=0)

# =========================================================================================== more experiments

# wifi test 1
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "wifi", steps= 8, limits=[-35, -75], 
              repeat=4, dir_name="experiment_wifi_1", wifi_str=[-69, 2], frequency=400, duration=4, calc_time=0)


# main experiment
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_main_experiment(main_client, 20, 15, limits_size=[0, 4000], duration=10, repeat=3, wifi_str=[-50, 2], dir_name="main_experiment2")
    organize_main_experiment_data(main_client, 20, 15, limits_size=[0, 4000], duration=10, wifi_str=[-50, 2], dir_name="main_experiment2")


# packet size test 3
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    limits_size = [4200, 10_000]
    steps = [int(limits_size[0]+(limits_size[1]-limits_size[0])*(i/(15-1))) for i in range(15)]
    run_main_experiment(main_client, 20, steps[9:], limits_size=[-1, -1], duration=10, repeat=3, wifi_str=[-50, 2], dir_name="main_experiment_large_packet")
    organize_main_experiment_data(main_client, 20, steps[:9], limits_size=[-1, -1], duration=10, wifi_str=[-50, 2], dir_name="main_experiment_large_packet", file_name="extra", show_graph=True)

    organize_main_experiment_data(main_client, 20, 15, limits_size=[0, 4000], duration=10, wifi_str=[-50, 2], dir_name="main_experiment2", file_name="dump", show_graph=True)





# packet size test 1
if __name__ == "__main__":
    main_client = c.ExperimentClient()
    main_client.startup_client()
    run_bunch(main_client, "ps", steps= 100, limits=[50, 2000], 
              repeat=6, dir_name="new_experiment_size_1", wifi_str=[-50, 2], frequency=400, duration=10, calc_time=0)


# packet size tesst 2
    limits = [1000, 10000]
    steppies = [int(limits[0]+(limits[1]-limits[0])*(i/(250-1))) for i in range(250)]
    run_bunch(main_client, "ps", steps= steppies[116:], limits=[1000, 10000], 
              repeat=6, dir_name="new_experiment_size_3", wifi_str=[-50, 2], frequency=400, duration=10, calc_time=0)
    

# frequency 1
    run_bunch(main_client, "hz", steps= 100, limits=[100, 5000], 
              repeat=6, dir_name="new_experiment_frequency_1", wifi_str=[-50, 2], message_size=350, duration=10, calc_time=0)

# frequency test 2
    run_bunch(main_client, "hz", steps= 100, limits=[100, 5000], 
              repeat=6, dir_name="new_experiment_frequency_2", wifi_str=[-50, 2], message_size=3500, duration=10, calc_time=0)