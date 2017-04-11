import numpy as np
import tqdm
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.evolution.evolution import Evolution
from broodwar_strategy_evolver.evolution.evolution import CrossoverMethod
import matplotlib.pyplot as plt

unit_repo = UnitRepository()

own_units = np.zeros(len(unit_repo.units))
own_units[unit_repo.get_by_name("Probe").id] = 18
own_units[unit_repo.get_by_name("Assimilator").id] = 1
own_units[unit_repo.get_by_name("Gateway").id] = 1
own_units[unit_repo.get_by_name("Cybernetics Core").id] = 1
own_units[unit_repo.get_by_name("Nexus").id] = 1
own_units[unit_repo.get_by_name("Pylon").id] = 3

'''
opp_units = np.zeros(len(unit_repo.units))
opp_units[unit_repo.get_by_name("Nexus").id] = 1
opp_units[unit_repo.get_by_name("Probe").id] = 4
opp_units[unit_repo.get_by_name("Zealot").id] = 0
opp_units[unit_repo.get_by_name("Dragoon").id] = 12
'''

opp_units = np.zeros(len(unit_repo.units))
opp_units[unit_repo.get_by_name("Drone").id] = 18
opp_units[unit_repo.get_by_name("Zergling").id] = 0
opp_units[unit_repo.get_by_name("Overlord").id] = 3
opp_units[unit_repo.get_by_name("Spawning Pool").id] = 1
opp_units[unit_repo.get_by_name("Hatchery").id] = 1

own_techs = np.zeros(len(unit_repo.techs))
own_upgrades = np.zeros(len(unit_repo.upgrades))

gamestate = GameState(own_race=Race.PROTOSS,
                      opp_race=Race.ZERG,
                      own_units=own_units,
                      opp_units=opp_units,
                      own_techs=own_techs,
                      own_upgrades=own_upgrades,
                      own_units_under_construction=[],
                      own_techs_under_construction=[],
                      own_upgrades_under_construction=[])

gamestate.frame = 24 * 60 * 4

minutes = 8
horizon = int(24*60*minutes)
print("Horizon=" + str(horizon))

evolution_a = None
evolution_b = None
evolution_c = None
evolution_d = None
evolution_e = None

tests = 50
generations = 100

fitness_a = []
fitness_b = []
fitness_c = []
fitness_d = []
fitness_e = []

samples_a = []
samples_b = []
samples_c = []
samples_d = []
samples_e = []

for g in range(generations+1):
    fitness_a.append(np.zeros(tests))
    fitness_b.append(np.zeros(tests))
    fitness_c.append(np.zeros(tests))
    fitness_d.append(np.zeros(tests))
    fitness_e.append(np.zeros(tests))

for test in tqdm.trange(tests):

    evolution_a = Evolution(gamestate=gamestate,
                            pop_size=64,
                            horizon=horizon,
                            crossover_method=CrossoverMethod.TWO_POINT,
                            bellman=2,
                            add_mutate_prob=0.5,
                            remove_mutate_prob=0.0,
                            swap_mutate_prob=0.0,
                            clone_mutate_prob=0.0,
                            chain_mutate_prob=0.0,
                            survival_rate=0.25)

    evolution_b = Evolution(gamestate=gamestate,
                            pop_size=64,
                            horizon=horizon,
                            crossover_method=CrossoverMethod.TWO_POINT,
                            bellman=2,
                            add_mutate_prob=0.0,
                            remove_mutate_prob=0.5,
                            swap_mutate_prob=0.0,
                            clone_mutate_prob=0.0,
                            chain_mutate_prob=0.0,
                            survival_rate=0.25)

    evolution_c = Evolution(gamestate=gamestate,
                            pop_size=64,
                            horizon=horizon,
                            crossover_method=CrossoverMethod.TWO_POINT,
                            bellman=2,
                            add_mutate_prob=0.0,
                            remove_mutate_prob=0.0,
                            swap_mutate_prob=0.5,
                            clone_mutate_prob=0.0,
                            chain_mutate_prob=0.0,
                            survival_rate=0.25)

    evolution_d = Evolution(gamestate=gamestate,
                            pop_size=64,
                            horizon=horizon,
                            crossover_method=CrossoverMethod.TWO_POINT,
                            bellman=2,
                            add_mutate_prob=0.0,
                            remove_mutate_prob=0.0,
                            swap_mutate_prob=0.0,
                            clone_mutate_prob=0.5,
                            chain_mutate_prob=0.0,
                            survival_rate=0.25)

    evolution_e = Evolution(gamestate=gamestate,
                            pop_size=64,
                            horizon=horizon,
                            crossover_method=CrossoverMethod.TWO_POINT,
                            bellman=2,
                            add_mutate_prob=0.5,
                            remove_mutate_prob=0.5,
                            swap_mutate_prob=0.5,
                            clone_mutate_prob=0.5,
                            chain_mutate_prob=0.0,
                            survival_rate=0.25)

    fitness_a[0][test] = evolution_a.genomes[0].fitness
    fitness_b[0][test] = evolution_b.genomes[0].fitness
    fitness_c[0][test] = evolution_c.genomes[0].fitness
    fitness_d[0][test] = evolution_d.genomes[0].fitness
    fitness_e[0][test] = evolution_e.genomes[0].fitness

    for gen in range(generations):

        evolution_a.update()
        fitness_a[gen+1][test] = evolution_a.genomes[0].fitness
        evolution_b.update()
        fitness_b[gen+1][test] = evolution_b.genomes[0].fitness
        evolution_c.update()
        fitness_c[gen+1][test] = evolution_c.genomes[0].fitness
        evolution_d.update()
        fitness_d[gen+1][test] = evolution_d.genomes[0].fitness
        evolution_e.update()
        fitness_e[gen+1][test] = evolution_e.genomes[0].fitness

        if gen == generations-1:
            samples_a.append(evolution_a.get_fitness())
            samples_b.append(evolution_b.get_fitness())
            samples_c.append(evolution_c.get_fitness())
            samples_d.append(evolution_d.get_fitness())
            samples_e.append(evolution_e.get_fitness())

avg_a = []
avg_b = []
avg_c = []
avg_d = []
avg_e = []
std_a = []
std_b = []
std_c = []
std_d = []
std_e = []

for gen_fit in fitness_a:
    avg_a.append(np.average(gen_fit))
    std_a.append(np.std(gen_fit))

for gen_fit in fitness_b:
    avg_b.append(np.average(gen_fit))
    std_b.append(np.std(gen_fit))

for gen_fit in fitness_c:
    avg_c.append(np.average(gen_fit))
    std_c.append(np.std(gen_fit))

for gen_fit in fitness_d:
    avg_d.append(np.average(gen_fit))
    std_d.append(np.std(gen_fit))

for gen_fit in fitness_e:
    avg_e.append(np.average(gen_fit))
    std_e.append(np.std(gen_fit))

g = np.array(range(generations+1), dtype=float)

a = np.array(avg_a, dtype=float)
s_a = np.array(std_a, dtype=float)
b = np.array(avg_b, dtype=float)
s_b = np.array(std_b, dtype=float)
c = np.array(avg_c, dtype=float)
s_c = np.array(std_c, dtype=float)
d = np.array(avg_d, dtype=float)
s_d = np.array(std_d, dtype=float)
e = np.array(avg_e, dtype=float)
s_e = np.array(std_e, dtype=float)


def save_result(name, fit_arr, std_arr):
    with open('comparisons/' + name + '_g_' + str(generations) + '_t_' + str(tests) + '.dat', 'w') as file:
        out = ""
        for i in range(len(fit_arr)):
            out += str(fit_arr[i]) + ";" + str(std_arr[i]) + "\n"
        file.write(out)


def save_samples(name, sam_arr):
    with open('comparisons/' + name + '_g_' + str(generations) + '_t_' + str(tests) + '.dat', 'w') as file:
        out = ""
        for i in range(len(sam_arr)):
            out += str(sam_arr[i]) + "\n"
        file.write(out)

save_result("add_mutation_w", a, s_a)
save_result("remove_mutation_w", b, s_b)
save_result("swap_mutation_w", c, s_c)
save_result("clone_mutation_w", d, s_d)
save_result("all_mutation_w", e, s_e)

save_samples("add_mutation_s", samples_a)
save_samples("remove_mutation_s", samples_b)
save_samples("swap_mutation_s", samples_c)
save_samples("clone_mutation_s", samples_d)
save_samples("all_mutation_s", samples_e)


#max_y = np.max([np.max(a) + np.max(s_a), np.max(b) + np.max(s_b), np.max(c) + np.max(s_c), np.max(d) + np.max(s_d), np.max(e) + np.max(s_e)])
#min_y = np.min([np.min(a) - np.max(s_a), np.min(b) - np.max(s_b), np.min(c) - np.max(s_c), np.min(d) - np.max(s_d), np.min(e) - np.max(s_e)])
max_y = np.max([np.max(a) + np.max(s_a), np.max(b) + np.max(s_b), np.max(c) + np.max(s_c), np.min(d) + np.max(s_d), np.max(e) + np.max(s_e)])
min_y = np.min([np.min(a) - np.max(s_a), np.min(b) - np.max(s_b), np.min(c) - np.max(s_c), np.min(d) - np.max(s_d), np.min(e) - np.max(s_e)])

#max_y = np.max([np.max(f) + np.max(s_f)])
#min_y = np.min([np.min(f) - np.max(s_f)])

plt.figure(figsize=(5, 4))

plt.ylim(ymin=min_y)
plt.ylim(ymax=max_y)
plt.xlim(xmax=generations)

plt.plot(g, a, color="red", label="Add mutation", linewidth=1.0, linestyle="dashed")
plt.fill_between(g, a-s_a, a+s_a, facecolor="red", alpha=0.10, linewidth=0.0)

plt.plot(g, b, color="blue", label="Remove mutation", linewidth=1.0, linestyle="solid")
plt.fill_between(g, b-s_b, b+s_b, facecolor="blue", alpha=0.10, linewidth=0.0)

plt.plot(g, c, color="green", label="Swap mutation", linewidth=1.0, linestyle="dotted")
plt.fill_between(g, c-s_c, c+s_c, facecolor="green", alpha=0.10, linewidth=0.0)

plt.plot(g, d, color="purple", label="Clone mutation", linewidth=1.0, linestyle="dashdot")
plt.fill_between(g, d-s_d, d+s_d, facecolor="purple", alpha=0.10, linewidth=0.0)

plt.plot(g, e, color="black", label="All mutations", linewidth=2.0, linestyle="solid")
plt.fill_between(g, e-s_e, e+s_e, facecolor="black", alpha=0.10, linewidth=0.0)

plt.ylabel('Fitness')
plt.xlabel('Generation')
plt.gcf().subplots_adjust(bottom=0.25)
plt.legend(loc='lower right', frameon=False)

#plt.show()
plt.savefig('comparisons/mutation_operators.png', dpi=500)

'''
print("-- A -- Fitness own=" + str(evolution_a.genomes[0].fitness))

print("-- Build order --")
for build in ForwardModel().trim(gamestate.clone(), evolution_a.genomes[0].build_order, horizon):
    print(build.name)

print("-- Resulting state --")
evolution_a.genomes[0].gamestate.print()

print("-- B -- Fitness own=" + str(evolution_b.genomes[0].fitness))

print("-- Build order --")
for build in ForwardModel().trim(gamestate.clone(), evolution_b.genomes[0].build_order, horizon):
    print(build.name)

print("-- Resulting state --")
evolution_b.genomes[0].gamestate.print()
'''