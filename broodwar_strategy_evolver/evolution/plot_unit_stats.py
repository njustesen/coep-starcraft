import numpy as np
import matplotlib.pyplot as plt
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.starcraft.adv_heuristics import heuristic

unit_repo = UnitRepository()

zealot = []
dragoon = []
dark_templar = []
marine = []
firebat = []
medic = []

frame = []
seconds = []
minutes = []

file = open("stats/unit_history_3.dat", 'r')
lines = []
for line in file:
    lines = line.split(" ")

for line in lines:
    records = line.split(";")
    i = -1
    for record in records:
        if i == -1:
            t = int(record.split(';')[0])
            frame.append(t / 1000 * 23.81)
            seconds.append(t / 1000 / 60)
            minutes.append(t / 1000)
        else:
            if i == unit_repo.get_by_name("Zealot").id:
                zealot.append(float(record))
            elif i == unit_repo.get_by_name("Dragoon").id:
                dragoon.append(float(record))
            elif i == unit_repo.get_by_name("Dark Templar").id:
                dark_templar.append(float(record))
            elif i == unit_repo.get_by_name("Marine").id:
                marine.append(float(record))
            elif i == unit_repo.get_by_name("Firebat").id:
                firebat.append(float(record))
            elif i == unit_repo.get_by_name("Medic").id:
                medic.append(float(record))
        i += 1

#plt.ylim(ymin=min_y)
#plt.ylim(ymax=max_y)
plt.figure(figsize=(10, 2))
plt.xlim(xmax=14000)
plt.xticks(np.arange(0, 14000+1, 1000))
plt.yticks(np.arange(0, 10+1, 2))
plt.ylim(ymin=0)
plt.ylim(ymax=10)
plt.gcf().subplots_adjust(bottom=0.25)

plt.plot(frame, zealot, color="red", label="Protoss Zealots", linewidth=1, linestyle="solid")
plt.fill_between(frame, 0, zealot, facecolor="red", alpha=0.10, linewidth=0.0)
plt.plot(frame, dragoon, color="red", label="Protoss Dragoons", linewidth=2, linestyle="solid")
plt.fill_between(frame, 0, dragoon, facecolor="red", alpha=0.10, linewidth=0.0)
#plt.plot(seconds, dark_templar, color="orange", label="Protoss Dark Templars", linewidth=2, linestyle="dotted")
plt.plot(frame, marine, color="blue", label="Terran Marines", linewidth=1, linestyle="dotted")
plt.fill_between(frame, 0, marine, facecolor="blue", alpha=0.10, linewidth=0.0)
plt.plot(frame, firebat, color="blue", label="Terran Firebats", linewidth=2, linestyle="dashdot")
plt.fill_between(frame, 0, firebat, facecolor="blue", alpha=0.10, linewidth=0.0)
#plt.plot(seconds, medic, color="blue", label="Terran Medics", linewidth=0.5, linestyle="dotted")

plt.ylabel('Unit Count')
plt.xlabel('Frame')

plt.legend(loc='best', frameon=False)

#plt.show()
plt.savefig('stats/unit_count_3.png', dpi=500)
