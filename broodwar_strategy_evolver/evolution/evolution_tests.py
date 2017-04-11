import numpy as np
import tqdm
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.evolution.evolution import Evolution
from broodwar_strategy_evolver.evolution.evolution import CrossoverMethod

unit_repo = UnitRepository()


def run(enemies, runs, generations):
    units = {}
    techs = {}
    upgrades = {}

    for s in tqdm.trange(runs):
        gamestate = GameState(own_race=Race.PROTOSS,
                              opp_race=Race.TERRAN,
                              own_units=own_units,
                              opp_units=enemies,
                              own_techs=own_techs,
                              own_upgrades=own_upgrades,
                              own_units_under_construction=[],
                              own_techs_under_construction=[],
                              own_upgrades_under_construction=[])

        gamestate.frame = 24 * 60 * 2

        minutes = 12
        horizon = int(24*60*minutes)
        print("Horizon=" + str(horizon))
        evolution = Evolution(gamestate=gamestate,
                              pop_size=64,
                              horizon=horizon,
                              crossover_method=CrossoverMethod.TWO_POINT,
                              bellman=2,
                              random_fitness=False,
                              survival_rate=0.25)

        for g in range(generations):
            evolution.update()

        champion = evolution.genomes[0]

        for i in range(len(champion.gamestate.units)):
            if i not in units.keys():
                units[i] = []
            units[i].append(champion.gamestate.units[i])
        for i in range(len(champion.gamestate.techs)):
            if i not in techs.keys():
                techs[i] = []
            techs[i].append(champion.gamestate.techs[i])
        for i in range(len(champion.gamestate.upgrades)):
            if i not in upgrades.keys():
                upgrades[i] = []
            upgrades[i].append(champion.gamestate.upgrades[i])

    for i in units.keys():
        avg = np.average(units[i])
        std = np.std(units[i])
        if avg == 0 and std == 0:
            continue
        try:
            print(unit_repo.get_by_id(i).name + ": " + str(avg) + " +/- " + str(std))
        except Exception as e:
            x = 0

    for i in techs.keys():
        avg = np.average(techs[i])
        std = np.std(techs[i])
        if avg == 0 and std == 0:
            continue
        try:
            print(unit_repo.get_by_id_and_type(i, Type.TECH).name + ": " + str(avg) + " +/- " + str(std))
        except Exception as e:
            x = 0

    for i in upgrades.keys():
        avg = np.average(upgrades[i])
        std = np.std(upgrades[i])
        if avg == 0 and std == 0:
            continue
        try:
            print(unit_repo.get_by_id_and_type(i, Type.UPGRADE).name + ": " + str(avg) + " +/- " + str(std))
        except Exception as e:
            x = 0


own_units = np.zeros(len(unit_repo.units))
own_units[unit_repo.get_by_name("Probe").id] = 10
own_units[unit_repo.get_by_name("Nexus").id] = 1
own_units[unit_repo.get_by_name("Pylon").id] = 1

opp_units_a = np.zeros(len(unit_repo.units))
opp_units_a[unit_repo.get_by_name("SCV").id] = 10
opp_units_a[unit_repo.get_by_name("Marine").id] = 10
opp_units_a[unit_repo.get_by_name("Firebat").id] = 0
opp_units_a[unit_repo.get_by_name("Vulture").id] = 0
opp_units_a[unit_repo.get_by_name("Goliath").id] = 0
opp_units_a[unit_repo.get_by_name("Battlecruiser").id] = 0
opp_units_a[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 0

opp_units_b = np.zeros(len(unit_repo.units))
opp_units_b[unit_repo.get_by_name("SCV").id] = 10
opp_units_b[unit_repo.get_by_name("Marine").id] = 0
opp_units_b[unit_repo.get_by_name("Firebat").id] = 10
opp_units_b[unit_repo.get_by_name("Vulture").id] = 0
opp_units_b[unit_repo.get_by_name("Goliath").id] = 0
opp_units_b[unit_repo.get_by_name("Battlecruiser").id] = 0
opp_units_b[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 0

opp_units_c = np.zeros(len(unit_repo.units))
opp_units_c[unit_repo.get_by_name("SCV").id] = 10
opp_units_c[unit_repo.get_by_name("Marine").id] = 0
opp_units_c[unit_repo.get_by_name("Firebat").id] = 0
opp_units_c[unit_repo.get_by_name("Vulture").id] = 8
opp_units_c[unit_repo.get_by_name("Goliath").id] = 0
opp_units_c[unit_repo.get_by_name("Battlecruiser").id] = 0
opp_units_c[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 0

opp_units_d = np.zeros(len(unit_repo.units))
opp_units_d[unit_repo.get_by_name("SCV").id] = 10
opp_units_d[unit_repo.get_by_name("Marine").id] = 0
opp_units_d[unit_repo.get_by_name("Firebat").id] = 0
opp_units_d[unit_repo.get_by_name("Vulture").id] = 4
opp_units_d[unit_repo.get_by_name("Goliath").id] = 0
opp_units_d[unit_repo.get_by_name("Battlecruiser").id] = 0
opp_units_d[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 4

opp_units_e = np.zeros(len(unit_repo.units))
opp_units_e[unit_repo.get_by_name("SCV").id] = 10
opp_units_e[unit_repo.get_by_name("Marine").id] = 0
opp_units_e[unit_repo.get_by_name("Firebat").id] = 0
opp_units_e[unit_repo.get_by_name("Vulture").id] = 0
opp_units_e[unit_repo.get_by_name("Goliath").id] = 4
opp_units_e[unit_repo.get_by_name("Battlecruiser").id] = 0
opp_units_e[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 4

opp_units_f = np.zeros(len(unit_repo.units))
opp_units_f[unit_repo.get_by_name("SCV").id] = 10
opp_units_f[unit_repo.get_by_name("Marine").id] = 0
opp_units_f[unit_repo.get_by_name("Firebat").id] = 0
opp_units_f[unit_repo.get_by_name("Vulture").id] = 0
opp_units_f[unit_repo.get_by_name("Goliath").id] = 0
opp_units_f[unit_repo.get_by_name("Battlecruiser").id] = 2
opp_units_f[unit_repo.get_by_name("Wraith").id] = 4
opp_units_f[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 0

own_techs = np.zeros(len(unit_repo.techs))
own_upgrades = np.zeros(len(unit_repo.upgrades))

run(opp_units_a, 50, 100)
run(opp_units_b, 50, 100)
run(opp_units_c, 50, 100)
run(opp_units_d, 50, 100)
run(opp_units_e, 50, 100)
run(opp_units_f, 50, 100)
