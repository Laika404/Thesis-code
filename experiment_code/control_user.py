#  this file represents a shell in which the user can directly interact with
# the experimental setup
import control_func as c



main_client = c.ExperimentClient()
main_client.startup_client()

# translation of the ch command which changes a single configuration
var_bind = {
    "time": "t",
    "frequency": "hz",
    "payload": "ps",
    "service": "qts",
    "calc-time": "ct"
}
def run_comm(command):
    match command[0]:
        case "start":
            main_client.send_start()
            print("start message send")
        case "stop":
            main_client.send_stop()
            print("stop message send")
        case "quit":
            main_client.end_all()
        case "off":
            main_client.send_off()
        case "check":
            main_client.send_check()
        case "ch":
            if len(command) == 3:
                if command[1] in var_bind.keys():
                        new_conf = main_client.get_config()
                        if command[1] == "time":
                            command[2] = int(float(command[2])*1000)
                        new_conf[var_bind[command[1]]] = int(command[2])
                        main_client.new_config(new_conf)
                else:
                    print("parameter does not exist")
            else:
                print("wrong amount of keywords")
        case "print":
            print(main_client.get_config())
        case _:
            print("command not recognized")

# control shell
print("CONTROL SHELL STARTED")
while True:
    new_comm = input("> ")
    run_comm(new_comm.split(" "))


