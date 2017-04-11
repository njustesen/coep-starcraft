import numpy as np
import matplotlib.pyplot as plt

fitness = []
frame = []
seconds = []
minutes = []

file = open("stats/fitness_history_3.dat", 'r')
for line in file:
    records = line.split(" ")
    for record in records:
        fitness.append(float(record.split(';')[1]))
        t = int(record.split(';')[0])
        frame.append(t / 1000 * 23.81)
        seconds.append(t / 1000)
        minutes.append(t / 1000 / 60)

pop_x = []
pop_y = []
file = open("stats/pop_history_3.dat", 'r')
for line in file:
    records = line.split(" ")
    for record in records:
        pop_x.append((float(record) / 1000 * 23.81))
        pop_y.append(100000)

update_x = []
update_y = []
file = open("stats/update_history_3.dat", 'r')
for line in file:
    records = line.split(" ")
    for record in records:
        update_x.append(float(record) / 1000 * 23.81)
        update_y.append(100000)

#plt.ylim(ymin=min_y)
#plt.ylim(ymax=max_y)
plt.figure(figsize=(10, 2))
plt.xlim(xmax=14000)
plt.xticks(np.arange(0, 14000+1, 1000))
plt.yticks(np.arange(0, 2500+1, 500))
plt.ylim(ymin=0)
plt.ylim(ymax=2500)
plt.gcf().subplots_adjust(bottom=0.25)

fake = []
for f in frame:
    fake.append(f*-1000)

#plt.bar(pop_x, pop_y, 0.5, color='black', alpha=0.50, label="Population reset")
plt.bar(update_x, update_y, 10, color='green',alpha=0.75)
plt.plot(frame, fitness, color="black", label="Fitness", linewidth=0.5, linestyle="solid")
plt.plot(frame, fake, color="green", label="Game state updates", linewidth=0.5, linestyle="solid")
plt.fill_between(frame, 0, fitness, facecolor="black", alpha=0.25, linewidth=0.0)
#plt.plot(pop_x, pop_y, 'ro', label="Population reset")
#plt.plot(pop_x, pop_y, 'g.', label="Population reset")

plt.ylabel('Fitness')
plt.xlabel('Frame')

plt.legend(loc='upper left', frameon=True)

#plt.show()
plt.savefig('stats/fitness_3.png', dpi=500)
plt.close()
