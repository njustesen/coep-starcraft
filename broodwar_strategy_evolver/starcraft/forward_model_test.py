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


def test_build_order(build_order, gamestate, to_frame=40000):
    print("-------------------")
    opp_units=np.zeros(len(unit_repo.units))
    gamestate, _ = forward_model.run(gamestate, build_order, to_frame=to_frame)
    gamestate.print

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
gamestate = GameState(Race.PROTOSS, Race.TERRAN, list(start_units), list(opp_units), own_techs=list(start_techs), own_upgrades=list(start_upgrades))

for i in range(100):
    test_build_order(
        create_build_order(["Probe", "Probe","Pylon", "Assimilator", "Gateway", "Cybernetics Core", "Probe", "Probe", "Zealot"]),
        gamestate.clone(),
        to_frame=3000
)