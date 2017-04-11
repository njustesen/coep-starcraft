import numpy as np
import tqdm
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.evolution.evolution import Evolution
from broodwar_strategy_evolver.evolution.evolution import CrossoverMethod
import matplotlib.pyplot as plt
import time

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

tests = 50
generations = 100

timing = []

for test in tqdm.trange(tests):

    evolution_a = Evolution(gamestate=gamestate,
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

    for gen in range(generations):

        start = millis = int(round(time.time() * 1000))
        evolution_a.update()
        t = int(round(time.time() * 1000)) - start
        timing.append(t)

print("Avg: + " + str(np.average(timing)) + ", +/- " + str(np.std(timing)))
