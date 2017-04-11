import numpy as np
import random
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel

unit_repo = UnitRepository()
forward_model = ForwardModel()
split = len(unit_repo.protoss)
norm = 64


class Stub:

    def __init__(self, build_order, units):
        self.build_order = build_order
        self.units_now = units

    def unit_build(self, a, b):
        for i in range(len(a)):
            if b[i] > a[i]:
                return i
        return None

    def update_units(self, units):
        unit = self.unit_build(self.units_now, units)
        if unit is not None:
            # Remove unit from build order
            for i in range(len(self.build_order)):
                if self.build_order[i] == unit:
                    self.build_order.pop(i)
                    break
        self.units_now = list(units)

    def update_populations(self, own_units, opp_units, frame, min, gas):
        self.update_units(own_units)

    def update(self):
        print("Stub update")

    def get_build_order(self):
        return self.build_order
