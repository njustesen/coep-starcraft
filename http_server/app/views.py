from django.http import HttpResponse
from django.shortcuts import render
import threading
import time
from broodwar_strategy_evolver.evolution.evolution import Evolution, CrossoverMethod, Genome
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
from broodwar_strategy_evolver.starcraft.forward_model import GameState, ForwardModel
from broodwar_strategy_evolver.evolution.stub import Stub
import numpy as np

unit_repo = UnitRepository()
lock = threading.Lock()
#evolution = Evolution(pop_size=32, own_race=Race.PROTOSS, opp_race=Race.TERRAN, horizon=24*60*8, coevolve=False)
forward_model = ForwardModel()


class Shared:
    def __init__(self):
        self.running = False
        self.build_order = []
        self.gamestate = None
        self.champion = None
        self.evolution = None
        self.generations = 100
        self.frames_per_build = 300
        self.start_time = 0
        self.pop_history = []
        self.update_history = []
        self.unit_history = []
        self.fitness_history = []
        self.timing = []
        self.time_started = 0

shared = Shared()


def run():
    print("Starting strategy evolution")
    while True:
        lock.acquire()
        shared.time_started = time.time() * 1000
        # Decrease frames_per_build if a lot of minerals
        if shared.gamestate.minerals > 500:
            max(20, shared.frames_per_build * 0.8)

        # Create new evolution
        minutes = 8
        horizon = int(23.81*60*minutes)
        shared.pop_history.append(int(round(time.time() * 1000 - shared.start_time)))
        shared.evolution = Evolution(gamestate=shared.gamestate,
                                     pop_size=64,
                                     horizon=horizon,
                                     bellman=2,
                                     crossover_method=CrossoverMethod.TWO_POINT,
                                     frames_per_build=shared.frames_per_build,
                                     survival_rate=0.25)

        # Transfer champion to new population
        if shared.champion is not None:
            shared.champion.protected
            shared.evolution.genomes[0] = shared.champion

        gen = 1
        lock.release()

        while gen <= shared.generations:
            #print("Thread acquiring lock")
            lock.acquire()
            #print("Thread acquired lock")
            #print(str(gen))
            if shared.gamestate.new_game:
                shared.champion = None
                shared.build_order = []
                lock.release()
                break
            fitness = shared.evolution.genomes[0].fitness
            shared.fitness_history.append([int(round(time.time() * 1000)) - shared.start_time, fitness])
            shared.evolution.update()
            gen += 1
            shared.champion = shared.evolution.genomes[0]

            #print("Thread releasing lock")
            lock.release()
            #print("Thread released lock")
            time.sleep(0.01)  # Give time to Django thread

        shared.timing.append((time.time() * 1000) - shared.time_started)

    return HttpResponse("Evolution stopped")


t1 = threading.Thread(target=run)


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


def probe(request):
    return HttpResponse("unit64")


def timing(request):
    lock.acquire()
    avg = np.average(shared.timing)
    std = np.std(shared.timing)
    out = str(avg) + " +/- " + str(std)
    lock.release()
    return HttpResponse(out)


def fitness_history(request):
    out = ""
    print("Acquiring lock")
    lock.acquire()
    print("Lock acquired")

    for frame in shared.fitness_history:
        out += str(frame[0]) + ";" + str(frame[1]) + "\n"

    lock.release()

    return HttpResponse(out)


def pop_history(request):
    out = ""
    print("Acquiring lock")
    lock.acquire()
    print("Lock acquired")

    for frame in shared.pop_history:
        out += str(frame) + "\n"

    lock.release()

    return HttpResponse(out)


def unit_history(request):
    out = ""
    print("Acquiring lock")
    lock.acquire()
    print("Lock acquired")

    for frame in shared.unit_history:
        t = frame[0]
        out += str(t) + ";"
        for unit in frame[1]:
            out += str(unit) + ";"
        out += "\n"

    lock.release()

    return HttpResponse(out)


def update_history(request):
    out = ""
    print("Acquiring lock")
    lock.acquire()
    print("Lock acquired")

    for frame in shared.update_history:
        out += str(frame) + "\n"

    lock.release()

    return HttpResponse(out)


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

    # If not knowledge of opponent
    if np.sum(opp_units) == 0:
        opp_units[unit_repo.get_worker(opp_race).id] = 10
        opp_units[unit_repo.get_base(opp_race).id] = 1

    # Update own game state
    gamestate = GameState(frame=frame,
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
                          new_game=new_game)

    # If no workers, just return a worker
    if gamestate.workers_minerals < 1:
        print("Nothing to do: return worker")
        build = unit_repo.get_worker(own_race)
    else:
        print(str(gamestate.workers_minerals) + " mineral workers.")
        build = __update__(gamestate)

    if build is None:
        print("No build found")
        return HttpResponse("-1")

    build_type = "unit"
    if build.type == Type.TECH:
        build_type = "tech"
    elif build.type == Type.UPGRADE:
        build_type = "upgr"

    out = build_type + str(build.id)
    print("Returning: " + out)

    return HttpResponse(out)


def __update__(gamestate):
    #print("Acquiring lock")
    lock.acquire()
    shared.update_history.append(int(round(time.time() * 1000 - shared.start_time)))
    #print("Lock acquired")
    if not shared.running:
        shared.gamestate = gamestate
        print("Starting thread")
        shared.start_time = int(round(time.time() * 1000))
        shared.running = True
        t1.start()
        print("Thread started")
    else:

        #print("Updating gamestate")

        # Update build order
        shared.gamestate = gamestate
        units = np.zeros(len(gamestate.units))
        for i in range(len(gamestate.units)):
            if gamestate.units[i] > 0:
                units[i] = gamestate.units[i]
        for i in range(len(gamestate.opp_units)):
            if gamestate.opp_units[i] > 0:
                units[i] = gamestate.opp_units[i]
        shared.unit_history.append((int(round(time.time() * 1000 - shared.start_time)), units))

        # If no workers or bases we lost
        if shared.gamestate.units[unit_repo.get_worker(shared.gamestate.race).id] == 0:
            if shared.gamestate.units[unit_repo.get_base(shared.gamestate.race).id] == 0:
                lock.release()
                return None
            lock.release()
            return unit_repo.get_worker(shared.gamestate.race)

        if shared.gamestate.new_game:
            lock.release()
            return unit_repo.get_worker(shared.gamestate.race)

        # Update build order and state of evolution
        shared.evolution.update_state(shared.gamestate)
        shared.champion = shared.evolution.genomes[0]
        shared.build_order = []
        out = "Build Order: "
        for build in shared.evolution.get_build_order(trimmed=True):
            shared.build_order.append(build)
            out += build.name + ", "
            if (build.type == Type.TECH or build.type == Type.UPGRADE) and shared.gamestate.units[build.id] > 0:
                out += " [ALREADY RESEARCHED!!!]"
        #print(out)

        if len(shared.build_order) > 0:
            print("Build: " + str(shared.build_order[0].name))
            shared.wait = False
            lock.release()
            return shared.build_order[0]
        shared.wait = False
        print("Returning: None")
    lock.release()
    return unit_repo.get_worker(shared.gamestate.race)


def monitor(request):
    context = {
        'key': 1,
    }
    return render(request, 'monitor.html', context)


def next_build(request):
    with lock:
        bo = shared.evolution.get_build_order()
        if len(bo) > 0:
            return HttpResponse(str(bo[0]))
        return HttpResponse("-1")


def get_build_order_ids(request):
    with lock:
        string_build_order = ""
        for build in shared.evolution.get_build_order():
            type = unit_repo.get_by_id(build)
            string_build_order += str(type.id) + ";"
            print(string_build_order)
        return HttpResponse(string_build_order)


def get_build_order(request):
    with lock:
        string_build_order = ""
        for build in shared.evolution.get_build_order():
            type = unit_repo.get_by_id(build)
            string_build_order += str((type.id, type.name)) + ";"
        print(string_build_order)
        return HttpResponse(string_build_order)


def index(request):
    return HttpResponse("Hello, world. You've reached the brood war strategy evolver.")
