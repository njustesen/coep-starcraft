import numpy as np
import tqdm
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.evolution.evolution import Evolution
from broodwar_strategy_evolver.evolution.evolution import CrossoverMethod

unit_repo = UnitRepository()

own_units = np.zeros(len(unit_repo.units))
own_units[unit_repo.get_by_name("Probe").id] = 9
own_units[unit_repo.get_by_name("Nexus").id] = 1

'''
opp_units = np.zeros(len(unit_repo.units))
opp_units[unit_repo.get_by_name("Nexus").id] = 1
opp_units[unit_repo.get_by_name("Probe").id] = 4
opp_units[unit_repo.get_by_name("Zealot").id] = 0
opp_units[unit_repo.get_by_name("Dragoon").id] = 12
'''

opp_units = np.zeros(len(unit_repo.units))
opp_units[unit_repo.get_by_name("Drone").id] = 9
opp_units[unit_repo.get_by_name("Zergling").id] = 0
opp_units[unit_repo.get_by_name("Hydralisk").id] = 0
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

gamestate.frame = 24 * 60 * 2

minutes = 8
horizon = int(24*60*minutes)
print("Horizon=" + str(horizon))
evolution = Evolution(gamestate=gamestate,
                      pop_size=64,
                      horizon=horizon,
                      crossover_method=CrossoverMethod.TWO_POINT,
                      bellman=2,
                      random_fitness=False,
                      survival_rate=0.25)

for g in tqdm.trange(50):
    evolution.update()

for genome in evolution.genomes:
    print("Fitness own=" + str(genome.fitness))

    print("-- Build order --")
    for build in ForwardModel().trim(gamestate.clone(), genome.build_order, horizon):
        print(build.name)

    print("-- Resulting state --")
    genome.gamestate.print()
    '''
    print("-- Checked state --")
    gamestate, _ = ForwardModel(verbose=True).run(gamestate.clone(), genome.build_order, horizon)
    gamestate.print()

    evolution.init_genome(genome, bellman=3)
    print("-- After init again --")
    genome.gamestate.print()
    '''

    break

