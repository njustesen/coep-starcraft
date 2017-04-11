from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
import numpy as np

# Unit table
unit_repo = UnitRepository()


def create_build_order(units):
    bo = []
    for unit in units:
        bo.append(unit_repo.get_by_name(unit))
    return bo


def test_build_order(build_order, gamestate):
    print("-------------------")
    opp_units=np.zeros(len(unit_repo.units))
    gamestate, _ = forward_model.run(gamestate, build_order, to_frame=50000)
    gamestate.print()

# Create Forward Model
forward_model = ForwardModel(verbose=True)

# Create initial unit vector
start_units = np.zeros(len(unit_repo.units)).astype(int)
start_units[unit_repo.get_worker(Race.PROTOSS).id] = 4
start_units[unit_repo.get_base(Race.PROTOSS).id] = 1

start_techs = np.zeros(len(unit_repo.techs)).astype(int)
start_upgrades = np.zeros(len(unit_repo.upgrades)).astype(int)

opp_units = np.zeros(len(unit_repo.units)).astype(int)
# Test PROTOSS Build Orders
test_build_order(
    create_build_order(["Probe", "Probe", "Assimilator", "Pylon", "Gateway", "Cybernetics Core", "Citadel of Adun", "Leg Enhancements", "Probe","Probe","Probe","Probe","Probe","Probe","Probe","Probe","Probe","Probe","Probe","Probe","Probe", "Leg Enhancements"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Probe", "Probe", "Probe", "Probe", "Assimilator", "Pylon", "Gateway", "Cybernetics Core", "Citadel of Adun", "Templar Archives", "High Templar", "High Templar", "Archon"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Probe", "Probe", "Probe", "Probe", "Assimilator", "Pylon", "Gateway", "Cybernetics Core", "Robotics Facility", "Robotics Support Bay", "Reaver", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab" ]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Probe", "Probe", "Probe", "Probe", "Assimilator", "Pylon", "Gateway", "Cybernetics Core", "Robotics Facility", "Robotics Support Bay", "Reaver", "Reaver", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab", "Scarab" ]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Nexus", "Assimilator", "Assimilator"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Assimilator"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Assimilator"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Probe", "Probe", "Probe", "Pylon", "Gateway", "Probe", "Zealot"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Zealot"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Probe", "Probe", "Probe", "Probe", "Probe", "Probe", "Probe", "Probe", "Probe"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Probe", "Probe", "Probe", "Pylon", "Gateway", "Probe", "Cybernetics Core", "Probe",
                        "Pylon", "Assimilator", "Probe", "Probe", "Dragoon"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
# TODO: FAILS
test_build_order(
    create_build_order(["Probe", "Pylon", "Gateway", "Assimilator", "Cybernetics Core", "Citadel of Adun", "Templar Archives", "Dark Templar", "Pylon", "Zealot", "Zealot", "Dark Archon"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Pylon", "Gateway", "Assimilator", "Cybernetics Core", "Citadel of Adun", "Templar Archives", "Dark Templar", "Dark Templar", "Pylon", "Zealot", "Zealot", "Dark Archon"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Pylon", "Gateway", "Assimilator", "Protoss Ground Weapons", "Forge", "Protoss Ground Weapons", "Protoss Ground Weapons"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Pylon", "Probe", "Carrier Capacity"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Probe", "Assimilator", "Assimilator"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["Probe", "Assimilator", "Nexus", "Probe", "Probe", "Probe", "Probe", "Probe", "Assimilator"]),
    GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
# TEST TERRAN BUILD ORDERS
start_units = np.zeros(len(unit_repo.units)).astype(int)
start_units[unit_repo.get_base(Race.TERRAN).id] = 1
start_units[unit_repo.get_worker(Race.TERRAN).id] = 4
test_build_order(
    create_build_order(["SCV", "Barracks", "Academy", "Refinery", "Comsat Station"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["SCV", "Barracks", "Academy", "Refinery", "Comsat Station", "Comsat Station"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["SCV", "Barracks", "Academy", "Refinery", "Command Center", "Comsat Station", "Comsat Station"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["SCV", "Barracks", "Refinery", "Factory", "Machine Shop", "Siege Tank Tank Mode"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["SCV", "Barracks", "Refinery", "Factory", "Spider Mines"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)

test_build_order(
    create_build_order(["SCV", "Barracks", "Refinery", "Factory", "Machine Shop", "Spider Mines"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
test_build_order(
    create_build_order(["SCV", "Barracks", "Refinery", "Factory", "Machine Shop", "Spider Mines", "Spider Mines"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
'''
# Create initial unit vector
units = np.zeros(len(unit_repo.units)).astype(int)
units[unit_repo.get_by_name("Forge").id] = 1
units[unit_repo.get_by_name("Nexus").id] = 1
units[unit_repo.get_by_name("Probe").id] = 6
units[unit_repo.get_by_name("Assimilator").id] = 1

techs = np.zeros(len(unit_repo.techs)).astype(int)
upgrades = np.zeros(len(unit_repo.upgrades)).astype(int)

units_under_construction = []
for i in range(len(unit_repo.units)):
    units_under_construction.append([])
units_under_construction[unit_repo.get_by_name("Dragoon").id] = [100,200,300,400]
units_under_construction[unit_repo.get_by_name("Photon Cannon").id] = [100]

techs_under_construction = []
for i in range(len(unit_repo.techs)):
    techs_under_construction.append([])
techs_under_construction[unit_repo.get_by_name("Psionic Storm").id] = [200]

upgrades_under_construction = []
for i in range(len(unit_repo.upgrades)):
    upgrades_under_construction.append([])
upgrades_under_construction[unit_repo.get_by_name("Protoss Ground Weapons").id] = [200]

# Test under production upgrade
test_build_order(
    create_build_order(["Protoss Ground Weapons"]),
    GameState(Race.TERRAN, Race.PROTOSS, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))
)
'''