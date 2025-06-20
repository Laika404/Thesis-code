# this file is used to generate a graph visualizing the preliminary test of the SensorSPHERE team

import matplotlib.pyplot as plt

with open("preliminary_data.txt") as file:
    data = file.readlines()[2:]

freq_data = []
pack_data = []
unit_amount = []

for line in data:
    num_list = "".join(line.split("|")).split()
    freq_data.append(float(num_list[1])/30)
    pack_data.append(100-float(num_list[3]))
    unit_amount.append(num_list[0])
plt.plot(freq_data, pack_data, 'o-')
for xi, yi, label in zip(freq_data, pack_data, unit_amount):
    plt.text(xi-10, yi + 1, str(label), ha='center', va='bottom', fontsize=12, color="red")
plt.grid(True)
plt.xlabel("message frequency (Hz)")
plt.ylabel("packet loss (%)")
plt.show()
