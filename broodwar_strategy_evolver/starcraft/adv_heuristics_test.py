from broodwar_strategy_evolver.starcraft.adv_heuristics import unit_heuristic, heuristic
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race
from broodwar_strategy_evolver.starcraft.forward_model import GameState
import random
import numpy as np

unit_repo = UnitRepository()

'''
# Simple test
unit_a = unit_repo.get_by_name("Marine")
unit_b = unit_repo.get_by_name("Zealot")
h = unit_heuristic(unit_a.id, unit_b.id)
print(str(h))

# State test
techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 2
units_a[unit_repo.get_by_name("Dragoon").id] = 1
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Marine").id] = 1
units_b[unit_repo.get_by_name("Firebat").id] = 2
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)

print("Terran = " + str(h))
techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 10
units_a[unit_repo.get_by_name("Dragoon").id] = 0
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Vulture").id] = 10
units_b[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 0
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)
print("Terran = " + str(h))

techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 0
units_a[unit_repo.get_by_name("Dragoon").id] = 10
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Vulture").id] = 0
units_b[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 5
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)
print("Terran = " + str(h))

techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 10
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Vulture").id] = 10
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)
print("Terran = " + str(h))

techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
upgrades_a[unit_repo.get_by_name("Leg Enhancements").id] = 1
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 10
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Vulture").id] = 10
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)
print("Terran = " + str(h))

techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
upgrades_a[unit_repo.get_by_name("Leg Enhancements").id] = 1
upgrades_a[unit_repo.get_by_name("Protoss Ground Weapons").id] = 1
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 10
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Vulture").id] = 10
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)
print("Terran = " + str(h))

print("PVP")
techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 20
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Reaver").id] = 5
units_b[unit_repo.get_by_name("Dark Templar").id] = 5
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)
print("Protoss = " + str(h))

print("Tanks")
techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Zealot").id] = 0
units_a[unit_repo.get_by_name("Dragoon").id] = 2
units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Vulture").id] = 0
units_b[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 1
h = heuristic(units_a, techs_a, upgrades_a, units_b)
print("Protoss = " + str(h))
h = heuristic(units_b, techs_a, upgrades_a, units_a)
print("Terran = " + str(h))
'''


print("Start")
techs_a = np.zeros(len(unit_repo.techs))
upgrades_a = np.zeros(len(unit_repo.upgrades))
units_a = np.zeros(len(unit_repo.units))
units_a[unit_repo.get_by_name("Marine").id] = 2
units_a[unit_repo.get_by_name("Firebat").id] = 1
units_a[unit_repo.get_by_name("Supply Depot").id] = 0

units_b = np.zeros(len(unit_repo.units))
units_b[unit_repo.get_by_name("Probe").id] = 0
units_b[unit_repo.get_by_name("Zealot").id] = 1
units_b[unit_repo.get_by_name("Dragoon").id] = 1

gamestate = GameState(Race.PROTOSS,
                      Race.TERRAN,
                      units_b,
                      units_a)

h = heuristic(gamestate)
print("A = " + str(h))
