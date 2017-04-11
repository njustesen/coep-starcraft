from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
import random
import os
import numpy as np

unit_repo = UnitRepository()
path = os.path.dirname(os.path.realpath(__file__))


def load_unit_heuristics(filename):
    h = {}

    file = open(filename, 'r')
    idx = 0
    b = []
    for line in file:
        # Race_b units
        if idx == 0:
            units = line.split('\n')[0].split(';')
            for u in units:
                if u != "":
                    unit = unit_repo.get_by_name(u)
                    b.append(unit.id)
                    h[unit.id] = {}
        else:
            # Race_a units
            cells = line.split('\n')[0].split(';')
            cell_idx = 0
            unit = None
            for cell in cells:
                if cell_idx == 0:
                    unit = unit_repo.get_by_name(cell)
                    if unit.id not in h:
                        h[unit.id] = {}
                else:
                    h[unit.id][b[cell_idx-1]] = float(cell)
                    h[b[cell_idx-1]][unit.id] = 2 - float(cell)
                cell_idx += 1

        idx += 1
    return h


def load_tech_upgrade_heuristics(filename):
    h_tech = {}
    h_upgrade = {}

    file = open(filename, 'r')
    idx = 0
    b = []
    for line in file:
        # Units
        if idx == 0:
            units = line.split('\n')[0].split(';')
            for u in units:
                if u != "":
                    unit = unit_repo.get_by_name(u)
                    b.append(unit.id)
                    h_tech[unit.id] = {}
                    h_upgrade[unit.id] = {}
        else:
            # Tech
            cells = line.split('\n')[0].split(';')
            cell_idx = 0
            research = None
            for cell in cells:
                if cell_idx == 0:
                    research = unit_repo.get_by_name(cell)
                    if research.type == Type.TECH:
                        h_tech[research.id] = {}
                    elif research.type == Type.UPGRADE:
                        h_upgrade[research.id] = {}
                elif cell != "":
                    if research.type == Type.TECH:
                        h_tech[research.id][b[cell_idx-1]] = float(cell)
                    elif research.type == Type.UPGRADE:
                        h_upgrade[research.id][b[cell_idx-1]] = float(cell)
                cell_idx += 1

        idx += 1
    return h_tech, h_upgrade


def load_costs():
    c = {}
    for unit in unit_repo.protoss:
        c[unit.id] = unit.minerals + unit.gas
    for unit in unit_repo.terran:
        c[unit.id] = unit.minerals + unit.gas
    return c

costs = load_costs()
unit_heuristics = load_unit_heuristics(path + "/data/unit_heuristics_8.csv")
tech_heuristics, upgrade_heuristics = load_tech_upgrade_heuristics(path + "/data/tech_upgrades_heuristics.csv")
worker_ids = [unit_repo.get_worker(Race.PROTOSS).id, unit_repo.get_worker(Race.TERRAN).id]
base_ids = [unit_repo.get_base(Race.PROTOSS).id, unit_repo.get_base(Race.TERRAN).id]
supplier_ids = [unit_repo.get_by_name("Pylon").id, unit_repo.get_by_name("Supply Depot").id]


def unit_heuristic(unit_a, unit_b):
    if unit_a in unit_heuristics and unit_b in unit_heuristics[unit_a]:
        return unit_heuristics[unit_a][unit_b]
    return 0.0


def decrease(x):
    return x ** 0.95


def heuristic(gamestate, banned_builds = [], restricted_builds = []):

    # Gather tech/upgrade ids
    techs = []
    upgrades = []
    for t in range(len(gamestate.techs)):
        if gamestate.techs[t] > 0:
            techs.append(t)
    for u in range(len(gamestate.upgrades)):
        if gamestate.upgrades[u] > 0:
            upgrades.append(u)

    # Unit bonuses
    unit_bonuses = {}
    for u in range(len(gamestate.units)):
        if gamestate.units[u] > 0:
            unit_bonuses[u] = 1.0
            for t in techs:
                if u in tech_heuristics and t in tech_heuristics[u]:
                    unit_bonuses[u] *= tech_heuristics[u][t]
            for up in upgrades:
                if up in upgrade_heuristics.keys() and u in upgrade_heuristics[up].keys():
                    unit_bonuses[u] *= upgrade_heuristics[up][u]

    # Count units
    sum_a = 0
    sum_b = 0
    for a in range(len(gamestate.units)):
        if gamestate.units[a] > 0 and a in unit_heuristics:
            if sum_b == 0:
                for b in range(len(gamestate.opp_units)):
                    if gamestate.opp_units[b] > 0 and b in unit_heuristics[a]:
                        sum_b += gamestate.opp_units[b]
            sum_a += gamestate.units[a]

    h_a = 0
    # Unit values
    for a in range(len(gamestate.units)):
        if gamestate.units[a] > 0 and a in unit_heuristics:
            for b in range(len(gamestate.opp_units)):
                if gamestate.opp_units[b] > 0 and b in unit_heuristics[a]:
                    h = unit_heuristic(a, b) * unit_bonuses[a]
                    p_a = gamestate.units[a] / sum_a
                    p_b = gamestate.opp_units[b] / sum_b
                    if a in worker_ids:
                        p_a = p_a / 2
                    if b in worker_ids:
                        p_b = p_b / 2
                    v_a = h * gamestate.opp_units[b] * gamestate.units[a] * (1-p_a)
                    v_b = (2-h) * gamestate.opp_units[b] * gamestate.units[a] * (1-p_b)
                    h_a += v_a - v_b

    useless_a = gamestate.bases * 14 - gamestate.workers_minerals # Too few workers/geysers on too many bases?

    # Useless pylons > 1/8 of supply
    unused_supplies = (gamestate.max_supply - gamestate.supply)
    accepted = (1.0/5.0)*gamestate.supply + 9
    useless_sup = max(0, unused_supplies - accepted)

    # Restricted Builds
    restricted = 0
    for restriction in restricted_builds:
        count = gamestate.units[unit_repo.get_by_name(restriction).id]
        if count > 0:
            restricted += count * 2

    return h_a - useless_a * 1 - useless_sup * 1 - restricted
