import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

min_depth = 1
max_depth = 6
actions1 = 1
actions2 = 2
actions3 = 3

depth = []
paragraphs1 = []
paragraphs2 = []
paragraphs3 = []

time1 = []
time2 = []
time3 = []

for i in range(min_depth, max_depth+1):
    depth.append(i)

    num_paragraps1 = i
    paragraphs1.append(num_paragraps1)
    time1.append(num_paragraps1 * 10)

    num_paragraps2 = ((actions2 ** i)-1) / (actions2-1)
    paragraphs2.append(num_paragraps2)
    time2.append(num_paragraps2 * 10)

    num_paragraps3 = ((actions3 ** i)-1) / (actions3-1)
    paragraphs3.append(num_paragraps3)
    time3.append(num_paragraps3 * 10)


fig, ax = plt.subplots(nrows=1, ncols=1)
plt.plot(depth, paragraphs1, label = "1 action")
plt.plot(depth, paragraphs2, label = "4 actions")
plt.plot(depth, paragraphs3, label = "7 actions")

#plt.title("Number of paragraphs for n action per story depth")
plt.legend()
ax.set_xlabel("Depth")
ax.set_ylabel("Total paragraphs")

def toTime(x):
    return x * 0.1

def fromTime(x):
    return x / 0.1

secax = ax.secondary_yaxis('right', functions=(toTime, fromTime))
secax.set_ylabel('Time in minutes')

#ax.set_yscale('log')
plt.show()
plt.close(fig)

