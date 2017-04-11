import numpy as np
import time

from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Type, Race
from http_server.sup import views

unit_repo = UnitRepository()
own_units = np.zeros(len(unit_repo.units)).astype(int)
own_units[unit_repo.get_by_name("Nexus").id] = 1
own_units[unit_repo.get_by_name("Probe").id] = 7

opp_units = np.zeros(len(unit_repo.units)).astype(int)
own_techs = np.zeros(len(unit_repo.techs)).astype(int)
own_upgrades = np.zeros(len(unit_repo.upgrades)).astype(int)


gamestate = GameState(own_race=Race.PROTOSS,
                      opp_race=Race.TERRAN,
                      own_units=own_units,
                      opp_units=opp_units,
                      minerals=50,
                      gas=0,
                      frame=0,
                      new_game=False)

# Get build from service
build = views.__update__(gamestate)
print("Building " + build)

# Print result
gamestate.print()
