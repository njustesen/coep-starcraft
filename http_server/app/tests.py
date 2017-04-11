import numpy as np
import time

from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Type, Race
from http_server.app import views

unit_repo = UnitRepository()
own_units = np.zeros(len(unit_repo.units)).astype(int)
own_units[unit_repo.get_by_name("Nexus").id] = 1
own_units[unit_repo.get_by_name("Probe").id] = 4

opp_units = np.zeros(len(unit_repo.units)).astype(int)
opp_units[unit_repo.get_by_name("Drone").id] = 4
opp_units[unit_repo.get_by_name("Hatchery").id] = 1
'''
opp_units[unit_repo.get_by_name("Barracks").id] = 1
opp_units[unit_repo.get_by_name("Academy").id] = 1
opp_units[unit_repo.get_by_name("Siege Tank Tank Mode").id] = 10
opp_units[unit_repo.get_by_name("Goliath").id] = 10
'''

own_techs = np.zeros(len(unit_repo.techs)).astype(int)
own_upgrades = np.zeros(len(unit_repo.upgrades)).astype(int)


gamestate = GameState(own_race=Race.PROTOSS,
                      opp_race=Race.ZERG,
                      own_units=own_units,
                      opp_units=opp_units,
                      minerals=50,
                      gas=0,
                      frame=0,
                      new_game=False)


# Run 100 steps of 100 frames
step_size = 10000
builds = []
for frame in range(50):

    # Construct observation from state
    own_units_under_construction = []
    for unit in unit_repo.units:
        own_units_under_construction.append([])
    own_techs_under_construction = []
    for tech in unit_repo.techs:
        own_techs_under_construction.append([])
    own_upgrades_under_construction = []
    for upgrade in unit_repo.upgrades:
        own_upgrades_under_construction.append([])

    for product in gamestate.under_production:
        if product.type.type == Type.BUILDING or product.type.type == Type.UNIT:
            own_units_under_construction[product.type.id].append(product.done_at - gamestate.frame)
        elif product.type.type == Type.TECH:
            own_techs_under_construction[product.type.id].append(product.done_at - gamestate.frame)
        elif product.type.type == Type.UPGRADE:
            own_upgrades_under_construction[product.type.id].append(product.done_at - gamestate.frame)

    gamestate = gamestate.clone()
    gamestate.units_under_construction = own_units_under_construction
    gamestate.techs_under_construction = own_techs_under_construction
    gamestate.upgrades_under_construction = own_upgrades_under_construction

    # Get build from service
    build = views.__update__(gamestate)

    # Build it
    if build is not None:
        builds.append(build)
        gamestate, _ = ForwardModel().run(gamestate, build_order=[build], to_frame=gamestate.frame + step_size)

    print(gamestate.frame)

    # Let evolution run a few iterations
    time.sleep(0.5)

gamestate.print()

print("- Build order -")
for build in builds:
    print(build.name)
