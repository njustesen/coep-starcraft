from django.http import HttpResponse
from django.shortcuts import render
import threading
import multiprocessing
import time
from broodwar_strategy_evolver.nn.ACNetwork import ACNetwork
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type, StarCraftException
from broodwar_strategy_evolver.starcraft.forward_model import GameState, ForwardModel
import operator
import collections
import numpy as np
import tensorflow as tf
import os
import math

# StarCraft config
unit_repo = UnitRepository()
fm = ForwardModel()
own_race = Race.PROTOSS
opp_race = Race.TERRAN
a_size = len(unit_repo.units_by_race(own_race)) + \
            len(unit_repo.techs_by_race(own_race)) + \
            len(unit_repo.upgrades_by_race(own_race))
s_size = a_size*3 + len(unit_repo.units_by_race(opp_race)) + 3

banned_builds = ["Shuttle", "Archon", "High Templar", "Dark Archon", "Carrier", "Reaver"]

print('Loading Model...')
sess = tf.Session()

hidden_layers = 4
hidden_nodes = 128
model_name = "supervised_" + str(hidden_layers) + "x" + str(hidden_nodes)
learning_rate = 0.001
trainer = tf.train.AdamOptimizer(learning_rate=learning_rate)
model = ACNetwork(s_size, a_size, "supervised", trainer, hidden_nodes=hidden_nodes, hidden_layers=hidden_layers, name=model_name)

# initialize the Session
sess = tf.Session()
model.restore(sess)


def split_to_int(arr):
    out = []
    for elm in arr.split("-"):
        out.append(int(elm))
    return out


def split_to_int_arr(arr):
    out = []
    for elm in arr.split("-"):
        inner_arr = []
        if elm != "":
            for inner in elm.split(","):
                inner_arr.append(int(inner))
        out.append(inner_arr)
    return out


def to_race(race_name):
    if race_name.lower() == "terran":
        return Race.TERRAN
    elif race_name.lower() == "protoss":
        return Race.PROTOSS
    elif race_name.lower() == "zerg":
        return Race.ZERG
    raise Exception("Unknown race (" + race_name + ")")


def build_is_available(build, state):
    #print(build.name + ": " + str(build.id))
    clone = state.clone()
    return len(fm.trim(clone, [build], state.frame+10000)) == 1


def __update__(state):

    print("----------------")

    # Make predictions
    v = state.to_vector(include_in_production=True, include_in_progress=True)
    preds = model.preds(sess, [v])

    # Remove illegal builds
    predictions = {}
    sum = 0
    for i in range(len(preds[0])):
        unit = unit_repo.get_by_race_idx(i, Race.PROTOSS)
        if build_is_available(unit, state) and unit.name not in banned_builds:
            predictions[unit.name] = preds[0][i]
            sum += preds[0][i]
        else:
            print(unit.name + ": " + str(preds[0][i]))

    # Normalize
    print("- Recalculating")
    p = []
    a = []
    for unit_name, pred in predictions.items():
        pred = pred / sum
        p.append(pred)
        unit = unit_repo.get_by_name(unit_name)
        a.append(unit)
        print(unit.name + ": " + str(pred))

    # Pick random action using probabilities
    build = np.random.choice(a, 1, p=p)[0]

    # Create output string
    build_type = "unit"
    if build.type == Type.TECH:
        build_type = "tech"
    elif build.type == Type.UPGRADE:
        build_type = "upgr"

    out = build_type + str(build.id)

    print("Returning: " + out)

    return out


def update(request):
    print("Update called.")

    # Parse input
    own_units = split_to_int(request.GET.get('own_units', ''))
    own_units_under_construction = split_to_int_arr(request.GET.get('own_units_under_construction', ''))
    own_techs = split_to_int(request.GET.get('own_techs', ''))
    own_techs_under_construction = split_to_int_arr(request.GET.get('own_techs_under_construction', ''))
    own_upgrades = split_to_int(request.GET.get('own_upgrades', ''))
    own_upgrades_under_construction = split_to_int_arr(request.GET.get('own_upgrades_under_construction', ''))
    opp_units = split_to_int(request.GET.get('opp_units', ''))
    minerals = int(request.GET.get('minerals', ''))
    own_race = to_race(request.GET.get('own_race', ''))
    opp_race = to_race(request.GET.get('opp_race', ''))
    gas = int(request.GET.get('gas', ''))
    frame = int(request.GET.get('frame', ''))
    new_game = request.GET.get('new_game', '') in ["True", "true"]
    game_over = request.GET.get('game_over', '') in ["True", "true"]
    won = request.GET.get('won', '') in ["True", "true"]
    id = int(request.GET.get('id', ''))

    # If not knowledge of opponent
    if np.sum(opp_units) == 0:
        opp_units[unit_repo.get_worker(opp_race).id] = 10
        opp_units[unit_repo.get_base(opp_race).id] = 1

    # Update own game state
    state = GameState(frame=frame,
                      minerals=minerals,
                      gas=gas,
                      own_units=own_units,
                      own_units_under_construction=own_units_under_construction,
                      own_techs=own_techs,
                      own_techs_under_construction=own_techs_under_construction,
                      own_upgrades=own_upgrades,
                      own_upgrades_under_construction=own_upgrades_under_construction,
                      opp_units=opp_units,
                      own_race=own_race,
                      opp_race=opp_race,
                      new_game=new_game,
                      game_over=game_over,
                      won=won)

    out = __update__(state)
    return HttpResponse(out)


def index(request):

    return HttpResponse("A3C for StarCraft.")
