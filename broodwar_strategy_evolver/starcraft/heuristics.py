from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
import random

unit_repo = UnitRepository()
split = len(unit_repo.protoss)
norm = 64


def supply_heuristic(frame):
    return prediction(frame, "supply")


def resource_heuristic(frame):
    return prediction(frame, "resources")


def resource_count(frame, race):
    #print("-- " + race + " --")
    min = 0
    gas = 0
    sup = 0
    for i in range(len(frame)):
        if (race == "protoss" and i < split) or (race == "terran" and i >= split):
            unit = unit_repo.get_unit_type(i)
            u_min = unit.minerals * frame[i] * norm
            u_gas = unit.gas * frame[i] * norm
            u_sup = unit.supply * frame[i] * norm
            sup += u_sup
            min += u_min
            gas += u_gas
            #if u_min > 0:
                #print(unit.name + ":" + str(u_min) + ":" + str(u_gas))
    return min, gas, sup


def random_heuristic(frame):
    return 1 if random.random() >= 0.5 else 0


def prediction(frame, method):
    a = 0
    b = 0
    idx = 0
    sum = 0
    #print("-------------------")
    for u in frame:
        v = unit_value(idx, method) * u * norm
        if idx < split:
            a += v
        else:
            b += v

        # DEBUG
        '''
        if v != 0:
            unit = unit_repo.get_unit_type(idx)
            print(unit.name + " : " + str(v))
        '''
        sum += v
        idx += 1
    # print("P: " + str((a / sum)))
    return a / sum


def unit_value(unit_idx, method):
    unit = unit_repo.get_by_idx(unit_idx)
    if method == "resources":
        return unit.minerals + unit.gas
    elif method == "supply":
        return unit.supply


def supply_heuristics(states):
    predictions = []
    for state in states:
        prediction = 0
        for unit_type in unit_repo.protoss:
            if unit_type.name != "Probe":
                prediction += unit_type.supply * state[unit_type.id]
        if self.coevolve:
            for unit_type in unit_repo.terran:
                if unit_type.name != "SCV":
                    prediction -= unit_type.supply * state[unit_type.id]
            # Normalize between 0 and 1
            prediction = (prediction + 200) / 400
        predictions.append(prediction)
    return predictions


def supply_heuristic(gamestate, units_b, race_b):
    prediction = 0
    for unit_type in unit_repo.units_by_race(gamestate.race):
        if unit_type.name != "Probe" and unit_type.name != "SCV":
            prediction += unit_type.supply * gamestate.units[unit_type.id]
    for unit_type in unit_repo.units_by_race(race_b):
        if unit_type.name != "Probe" and unit_type.name != "SCV":
            prediction -= unit_type.supply * units_b[unit_type.id]

    if self.coevolve:
        # Normalize between 0 and 1
        prediction = (prediction + 200) / 400

    return prediction


def complex_heuristics(self, gamestate, units_b, race_b):
      return 1