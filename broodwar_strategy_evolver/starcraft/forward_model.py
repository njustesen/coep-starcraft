from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type, StarCraftException
import random
import sys
import numpy as np

mineral_speed = 0.050   # Minerals per frame per worker
gas_speed = 0.070       # Gas per frame per worker
building_time = 50      # Frames it takes to move worker to building location
expand_time = 50        # Frames it takes to move worker to expansion location

frames_per_build = 300  # Used by random build order generation

unit_repo = UnitRepository()


class Build:

    def __init__(self, type, done_at, produced_at=None, done=False):
        self.type = type
        self.produced_at = produced_at
        self.done_at = done_at
        self.done = done


class GameState:

    def __init__(self,
                 own_race,
                 opp_race,
                 own_units,
                 opp_units,
                 minerals=50,
                 gas=0,
                 frame=0,
                 own_units_under_construction=[],
                 own_techs=[],
                 own_techs_under_construction=[],
                 own_upgrades=[],
                 own_upgrades_under_construction=[],
                 new_game=False,
                 game_over=False,
                 won=False):
        self.game_over = game_over
        self.won = won
        self.race = own_race
        self.opp_race = opp_race
        self.units = list(own_units)
        self.opp_units = list(opp_units)
        self.techs = list(own_techs)
        self.upgrades = list(own_upgrades)
        if len(self.techs) == 0:
            self.techs = np.zeros(len(unit_repo.techs)).astype(int)
        if len(self.upgrades) == 0:
            self.upgrades = np.zeros(len(unit_repo.upgrades)).astype(int)
        self.race = own_race
        self.minerals = minerals
        self.gas = gas
        self.supply = self.get_supply()
        self.max_supply = self.get_max_supply()
        self.workers = self.get_workers()
        self.workers = max(self.workers-1, 0)  # Save one worker for building and scouting
        self.bases = self.get_bases()
        self.geysers = self.get_gas_geysers()
        self.workers_gas = max(0, min(self.workers, self.geysers*3))
        self.workers_minerals = max(0, self.workers-self.workers_gas)
        self.frame = frame
        self.new_game = new_game
        self.units_under_construction = own_units_under_construction
        self.techs_under_construction = own_techs_under_construction
        self.upgrades_under_construction = own_upgrades_under_construction
        self.under_production = self.get_under_production(own_units_under_construction,
                                                          own_techs_under_construction,
                                                          own_upgrades_under_construction)

    def clone(self):
        clone = GameState(self.race, self.opp_race, list(self.units), list(self.opp_units),
                          own_techs=list(self.techs), own_upgrades=list(self.upgrades),
                          minerals=self.minerals, gas=self.gas, frame=self.frame, new_game=self.new_game)
        clone.supply = self.supply
        clone.max_supply = self.max_supply
        clone.workers = self.workers
        clone.bases = self.bases
        clone.geysers = self.geysers
        clone.workers_gas = self.workers_gas
        clone.workers_minerals = self.workers_minerals

        clone.under_production = []
        for product in self.under_production:
            clone.under_production.append(Build(product.type, done_at=product.done_at, produced_at=product.produced_at, done=product.done))

        clone.units_under_construction = list(self.units_under_construction)
        clone.techs_under_construction = list(self.techs_under_construction)
        clone.upgrades_under_construction = list(self.upgrades_under_construction)

        return clone

    def to_vector(self, include_in_production=False, include_in_progress=False, minerals=False, gas=False, supply=True):
        r_arr = []
        if minerals:
            r_arr.append(min(1.0, self.minerals/1000))
        if gas:
            r_arr.append(min(1.0, self.gas/1000))
        if supply:
            r_arr.append(min(1.0, (self.max_supply - self.supply) / 16))
            r_arr.append(self.supply/200)
            r_arr.append(self.max_supply/200)

        u_arr = []
        for unit in unit_repo.units_by_race(self.race):
            u = self.units[unit.id]
            u_arr.append(min(1.0, u/64))
        t_arr = []
        for tech in unit_repo.techs_by_race(self.race):
            t = self.techs[tech.id]
            t_arr.append(min(1.0, t/64))
        up_arr = []
        for up in unit_repo.upgrades_by_race(self.race):
            up = self.upgrades[up.id]
            up_arr.append(min(1.0, up/64))
        o_arr = []
        for unit in unit_repo.units_by_race(self.opp_race):
            o = self.opp_units[unit.id]
            o_arr.append(min(1.0, o/64))
        if include_in_production or include_in_progress:
            l = len(unit_repo.units_by_race(self.race) + unit_repo.techs_by_race(self.race) + unit_repo.upgrades_by_race(self.race))
            prod_arr = np.zeros(l)
            prog_arr = np.zeros(l)
            for build in self.under_production:
                if not build.done:
                    idx = unit_repo.get_by_name(build.type.name).idx
                    prod_arr[idx] += 1
                    progress = (build.type.build_time - (build.done_at - self.frame)) / build.type.build_time
                    prog_arr[idx] = max(prog_arr[idx], progress)
            p_arr = []
            if include_in_production:
                for prod in prod_arr:
                    p_arr.append(min(1, prod/16))
            if include_in_progress:
                p_arr.extend(prog_arr)
            return u_arr + t_arr + up_arr + p_arr + o_arr + r_arr
        return u_arr + t_arr + up_arr + o_arr + r_arr

    def from_vector(self, vector):
        for unit in unit_repo.units_by_race(self.race):
            self.units[unit.id] = vector[unit.idx] * 64
        for tech in unit_repo.techs_by_race(self.race):
            self.techs[tech.id] = vector[tech.idx]
        for upgrade in unit_repo.upgrades_by_race(self.race):
            self.upgrades[upgrade.id] = vector[upgrade.idx]
        start = len(unit_repo.units_by_race(self.race) + unit_repo.techs_by_race(self.race) + unit_repo.upgrades_by_race(self.race))
        for idx in range(start):
            if vector[start + idx] > 0:
                unit = unit_repo.get_by_idx(idx)
                self.under_production.append(Build(type=unit, done_at=self.frame+unit.build_time, produced_at=unit.build_at, done=False))
        for unit in unit_repo.units_by_race(self.opp_race):
            if vector[start + start + start + unit.idx] > 0:
                self.opp_units[unit.id] = vector[start + start + start + unit.idx] * 64

        #self.minerals = vector[-1] * 1000
        #self.gas = vector[-2] * 1000
        self.supply = vector[-1] * 200
        self.max_supply = vector[-2] * 200

    def get_under_production(self, units, techs, upgrades):
        under_production = []
        id = 0
        for unit in units:
            for time_left in unit:
                type = unit_repo.get_by_id(id)
                build = Build(type, done_at=self.frame + time_left, produced_at=unit_repo.get_by_id(type.build_at))
                under_production.append(build)
            id += 1
        id = 0
        for tech in techs:
            for time_left in tech:
                if time_left != 0:
                    type = unit_repo.get_by_id_and_type(id, Type.TECH)
                    build = Build(type, done_at=self.frame + time_left, produced_at=unit_repo.get_by_id(type.build_at))
                    under_production.append(build)
            id += 1
        id = 0
        for upgrade in upgrades:
            for time_left in upgrade:
                if time_left != 0:
                    type = unit_repo.get_by_id_and_type(id, Type.UPGRADE)
                    build = Build(type, done_at=self.frame + time_left, produced_at=unit_repo.get_by_id(type.build_at))
                    under_production.append(build)
            id += 1
        return under_production

    def time_when_build(self, id):
        time = sys.maxsize
        for product in self.under_production:
            if not product.done and (product.type.type == Type.BUILDING or product.type.type == Type.UNIT) and product.type.id == id:
                time = min(time, product.done_at)
        if time == sys.maxsize:
            raise StarCraftException("[" + unit_repo.get_by_id(id).name + "] Requirement is not under construction!")
        return time

    def same_unit(self, a, b):
        if a is None or b is None:
            return False
        return a.id == b.id and a.type == b.type

    def time_to_produce(self, unit, force=False):

        time = self.frame

        # Requirements
        requirements_available = self.frame
        reqs = unit.requires
        for req in reqs:
            if self.units[req] == 0 and not force:
                done_at = self.time_when_build(req)
                requirements_available = max(requirements_available, done_at)

        # Assimilator deadlock?
        if unit.name == unit_repo.get_geyser(self.race).name and not force:
            workers_available = sys.maxsize
            in_production = 0
            for product in self.under_production:
                if product.done:
                    continue
                if product.type.name == unit_repo.get_worker(self.race).name:
                    workers_available = min(workers_available, product.done_at)
                    in_production += 1
                if product.type.name == unit_repo.get_geyser(self.race).name:
                    in_production -= 3
            if self.workers_minerals + in_production <= 3:
                raise StarCraftException("Not enough workers to support another geyser!")
            elif self.workers_minerals <= 3:
                requirements_available = max(requirements_available, workers_available)

        # Gas geysers available
        if unit.name == unit_repo.get_geyser(self.race).name and not force:
            spots = self.units[unit_repo.get_base(self.race).id] - self.geysers
            spot_available = sys.maxsize
            for product in self.under_production:
                if product.type.name == unit_repo.get_geyser(self.race).name:
                    spots -= 1
                elif product.type.name == unit_repo.get_base(self.race).name or product.type.name == unit_repo.get_base(self.race).name:
                    spots += 1
                    spot_available = min(spot_available, product.done_at)
            if self.geysers >= spots:
                if spot_available != sys.maxsize:
                    requirements_available = max(requirements_available, spot_available)
                else:
                    raise StarCraftException("No free spots for gas geyser!")

        # Available supply
        supply_available = self.frame
        if self.supply + unit.supply > self.max_supply and unit.type == Type.UNIT:  # TODO: Check rules
            supply_available = sys.maxsize
            for product in self.under_production:
                if not product.done:
                    if product.type.name == "Pylon" or product.type.name == "Supply Depot" or product.type.name == "Nexus" or product.type.name == "Command Center":
                        supply_available = min(supply_available, product.done_at)
            if supply_available == sys.maxsize:
                raise StarCraftException("Build will never be build (supplies)!")

        # Available resources
        resources_available = self.frame
        # Don't harvest first 6 seconds of game
        bonus_frames = (6 * 24 - min(6 * 24, self.frame))
        if unit.minerals > self.minerals:
            if not force:
                if self.workers_minerals == 0:
                    raise StarCraftException("Unit requires minerals and no mineral workers available.")
                resources_available = max(resources_available, self.frame + bonus_frames + (unit.minerals - self.minerals) / (mineral_speed * self.effective_min_workers()))
            else:
                self.minerals = unit.minerals
        if unit.gas > self.gas:
            if self.geysers > 0 and self.workers_gas > 0:
                if not force:
                    resources_available = max(resources_available, self.frame + bonus_frames + (unit.gas - self.gas) / (gas_speed * self.workers_gas))
                    # TODO: Add gas gathered from new geysers in production
                else:
                    self.gas = unit.gas
            else:
                resources_available = sys.maxsize
                for product in self.under_production:
                    if not product.done and product.type.name == "Assimilator" or product.type.name == "Refinery":
                        to_gas = min(self.workers_minerals, 3)
                        resources_available = min(resources_available, product.done_at + (unit.gas - self.gas) / (gas_speed * to_gas))
                if resources_available == sys.maxsize and not force:
                    raise StarCraftException("Unit requires gas and no gas available or under construction.")
            if resources_available > time and force:
                self.gas = unit.gas
                resources_available = time

        # Available production buildings
        building_available = self.frame
        if unit.type != Type.BUILDING and not force:
            if unit.build_at == -2:
                raise StarCraftException("Unit or research of this type cannot be build! (" + unit.name + ")")
            building_available = sys.maxsize
            used = 0
            have = self.units[unit.build_at]
            add_on = None
            add_ons = 0
            add_ons_used = 0
            add_on_required = False
            #print("Build at: " + str(type.build_at))
            if unit_repo.get_by_id(unit.build_at).name == "Factory":
                add_on = unit_repo.get_by_name("Machine Shop")
                add_ons = self.units[add_on.id]
            elif unit_repo.get_by_id(unit.build_at).name == "Starport":
                add_on = unit_repo.get_by_name("Control Tower")
                add_ons = self.units[add_on.id]
            add_on_required = unit.name in ["Siege Tank Tank Mode", "Dropship", "Science Vessel"]
            for product in self.under_production:
                if not product.done:
                    if product.type.type == Type.BUILDING or product.type.type == Type.UNIT:
                        if product.type.id == unit.build_at and not add_on_required:
                            building_available = min(building_available, product.done_at)
                        elif add_on_required and product.type.id == add_on:
                            building_available = min(building_available, product.done_at)
                    if product.produced_at is not None and product.produced_at.id == unit.build_at:    # TODO: Can add-on and units be produced at same time?
                        used += 1
                        building_available = min(building_available, product.done_at)
                        if product.type.name == "Siege Tank Tank Mode":
                            add_ons_used += 1
                        if product.type.name == "Dropship" or product.type.name == "Science Vessel":
                            add_ons_used += 1
            if have > used and (not add_on_required or add_ons > add_ons_used):
                building_available = self.frame

            if building_available == sys.maxsize:
                raise StarCraftException("No production buildings available!")

        # Special units
        special_available = self.frame
        spe_count = 0
        spe_mul = 0
        spe_unit = ""
        if unit.name == "Archon": spe_count, spe_unit = 2, "High Templar"
        if unit.name == "Dark Archon": spe_count, spe_unit = 2, "Dark Templar"
        if unit.name == "Interceptor": spe_mul, spe_unit = 8, "Carrier"
        if unit.name == "Scarab": spe_mul, spe_unit = 5, "Reaver"
        if unit.name == "Nuclear Missile": spe_mul, spe_unit = 1, "Nuclear Silo"

        if spe_unit != "" and not force:
            needs = 0
            spe_unit = unit_repo.get_by_name(spe_unit)
            if spe_count > 0:
                if self.units[spe_unit.id] < spe_count:
                    needs = spe_count - self.units[spe_unit.id]
            elif spe_mul > 0:
                if self.units[unit.id] <= spe_mul * self.units[spe_unit.id]:
                    needs = (self.units[unit.id] - spe_mul * self.units[spe_unit.id]) + 1
            found = 0
            if needs > 0:
                special_available = sys.maxsize  # Pessimistic search
                for product in self.under_production:
                    if not product.done and (product.type.type == Type.BUILDING or product.type.type == Type.UNIT) and product.type.id == spe_unit.id:
                        special_available = min(product.done_at, special_available)
                        found += 1
                    if not product.done and (product.type.type == Type.BUILDING or product.type.type == Type.UNIT) and product.type.id == unit.id:
                        found -= 1

                if special_available == sys.maxsize or found < needs:
                    raise StarCraftException(unit_repo.get_by_id(unit.id).name + " requires " + str(needs) + " more " + spe_unit.name + "s - none in production!")

        # Add-ons
        add_on_base = ""
        other_add_on = ""
        if unit.name == "Comsat Station": add_on_base, other_add_on = "Command Center", "Nuclear Silo"
        if unit.name == "Nuclear Silo": add_on_base, other_add_on = "Command Center", "Comsat Station"
        if unit.name == "Control Tower": add_on_base = "Starport"
        if unit.name == "Covert Ops": add_on_base, other_add_on = "Science Facility", "Physics Lab"
        if unit.name == "Physics Lab": add_on_base, other_add_on = "Science Facility", "Physics Lab"
        if unit.name == "Machine Shop": add_on_base = "Factory"
        add_on_available = self.frame
        if add_on_base != "" and not force:
            add_on_available = sys.maxsize
            other = unit_repo.get_by_name(other_add_on) if other_add_on != "" else None
            base = unit_repo.get_by_name(add_on_base)
            other_count = self.units[other.id] if other_add_on != "" else 0
            under_production = 0
            for product in self.under_production:
                if not product.done and (product.type.type == Type.BUILDING or product.type.type == Type.UNIT) and ((other is not None and product.type.id == other.id) or product.type.id == unit.id):
                    under_production += 1
            if self.units[unit.id] + other_count + under_production < self.units[base.id]:
                add_on_available = self.frame
            else:
                for product in self.under_production:
                    if not product.done and (product.type.type == Type.BUILDING or product.type.type == Type.UNIT) and product.type.id == base.id:
                        add_on_available = min(add_on_available, product.done_at)
            if add_on_available == sys.maxsize:
                raise StarCraftException("Add on " + unit.name + " has no base building (" + base.name + ") - and is not under construction.")

        # Already researched tech or upgrade?
        if unit.type == Type.TECH:
            if self.techs[unit.id] > 0:
                raise StarCraftException("Tech already researched.")
            for product in self.under_production:
                if product.type.id == unit.id and product.type.type == unit.type:
                    raise StarCraftException("Tech is already being researched.")
        if unit.type == Type.UPGRADE and not force:
            if self.upgrades[unit.id] > 0:
                raise StarCraftException("Upgrade already researched.")
            for product in self.under_production:
                if product.type.id == unit.id and product.type.type == unit.type:
                    raise StarCraftException("Upgrade is already being researched.")

        # Max 3 bases
        if unit.id == unit_repo.get_base(self.race).id and not force:
            bases = self.units[unit.id]
            for product in self.under_production:
                if not product.done and product.type.id == unit.id:
                    bases += 1
            if bases >= 3:
                raise StarCraftException("No more than 3 expansions.")

        # Final time is when all requirements are met
        time = max([requirements_available, supply_available, resources_available, building_available,
                    special_available, add_on_available])

        return time

    def build(self, unit):

        if unit.build_at == -2:
            raise StarCraftException("Cannot build this building! (" + unit.name + ")")

        if round(self.minerals) < unit.minerals or round(self.gas) < unit.gas:
            raise StarCraftException("Not enough resources! min=" + str(self.minerals) + " (" + str(unit.minerals) + "), gas=" + str(self.gas) + " (" + str(unit.gas) + ")")

        if self.supply + unit.supply > self.max_supply:
            raise StarCraftException("Not enough supply! sup=" + str(self.supply) + "/" + str(self.max_supply) + " ( " + str(unit.supply) + ")")

        if self.supply + unit.supply > 200:
            raise StarCraftException("Supply limit reached!")

        # Special units
        if unit.name == "Dark Archon":
            if self.units[unit_repo.get_by_name("Dark Templar").id] >= 2:
                self.units[unit_repo.get_by_name("Dark Templar").id] -= 2
            else:
                raise StarCraftException("Dark Archon requires two Dark Templars!")

        if unit.name == "Archon":
            if self.units[unit_repo.get_by_name("High Templar").id] >= 2:
                self.units[unit_repo.get_by_name("High Templar").id] -= 2
            else:
                raise StarCraftException("Archon requires two High Templars!")

        if unit.name == "Interceptor":
            interceptors = self.units[unit_repo.get_by_name("Interceptor").id]
            carriers = self.units[unit_repo.get_by_name("Carrier").id]
            if interceptors >= carriers * 8:     # TODO: +4 when upgraded
                raise StarCraftException("Not enough carriers to build interceptors!")

        if unit.name == "Scarab":
            scarabs = self.units[unit_repo.get_by_name("Scarab").id]
            reavers = self.units[unit_repo.get_by_name("Reaver").id]
            if scarabs >= reavers * 5:     # TODO: +4 when upgraded
                raise StarCraftException("Not enough reavers to build scarabs!")

        # Add-ons
        add_on_base = ""
        other_add_on = ""
        if unit.name == "Comsat Station": add_on_base, other_add_on = "Command Center", "Nuclear Silo"
        if unit.name == "Nuclear Silo": add_on_base, other_add_on = "Command Center", "Comsat Station"
        if unit.name == "Control Tower": add_on_base = "Starport"
        if unit.name == "Covert Ops": add_on_base, other_add_on = "Science Facility", "Physics Lab"
        if unit.name == "Physics Lab": add_on_base, other_add_on = "Science Facility", "Physics Lab"
        if unit.name == "Machine Shop": add_on_base = "Factory"
        if add_on_base != "":
            add_on_available = sys.maxsize
            other = unit_repo.get_by_name(other_add_on) if other_add_on != "" else None
            other_count = self.units[other.id] if other_add_on != "" else 0
            base = unit_repo.get_by_name(add_on_base)
            if self.units[unit.id] + other_count >= self.units[base.id]:
                raise StarCraftException("No base " + base.name + " for add-on " + unit.name)

        # Produce if no exceptions
        #print("Producing " + type.name + " at t=" + str(self.t) + " [" + str(self.t / 23.81) + " s], min=" + str(self.minerals) + ", gas=" + str(self.gas))
        build = Build(type=unit, done_at=self.frame + unit.build_time, produced_at=unit_repo.get_by_id(unit.build_at))
        self.under_production.append(build)
        self.minerals -= unit.minerals
        self.gas -= unit.gas
        self.supply += unit.supply

    def progress(self, t):
        steps = t - self.frame

        # Don't harvest first 6 seconds of game
        mine_steps = max(0, t - self.frame)
        self.minerals += mine_steps * mineral_speed * self.effective_min_workers()
        self.gas += mine_steps * gas_speed * self.workers_gas
        self.frame += steps

        for product in self.under_production:
            if not product.done and t >= product.done_at:
                product.done = True
                #print(type.name + " completed at t=" + str(product.done_at) + " [" + str(product.done_at / 23.81) + " s]")
                if product.type.name == "Pylon" or product.type.name == "Supply Depot":
                    self.max_supply += 8
                elif product.type.name == "Nexus" or product.type.name == "Command Center":
                    self.max_supply += 9
                    self.bases += 1
                elif product.type.name == "Assimilator" or product.type.name == "Refinery":
                    to_gas = min(max(0, self.workers_minerals), 3)
                    self.workers_minerals -= to_gas
                    self.workers_gas += to_gas
                    self.geysers += 1
                    # Gather gas on extra geyser
                    self.gas += (t - product.done_at) * gas_speed * to_gas
                elif product.type.name == "SCV" or product.type.name == "Probe":
                    self.workers += 1
                    if self.workers_minerals < 6:  # Is this true?
                        self.workers_minerals += 1
                    elif self.workers_gas < self.geysers * 3:
                        self.workers_gas += 1
                    else:
                        self.workers_minerals += 1
                if product.type.type == Type.UNIT or product.type.type == Type.BUILDING:
                    self.units[product.type.id] += 1
                elif product.type.type == Type.TECH:
                    self.techs[product.type.id] += 1
                elif product.type.type == Type.UPGRADE:
                    self.upgrades[product.type.id] += 1

    def finish(self, limit):
        end = self.frame
        for product in self.under_production:
            if not product.done and product.done_at <= limit:
                end = max(end, product.done_at)
        self.progress(end)

    def effective_min_workers(self):
        if self.bases < 1:
            return 0
        workers = self.workers_minerals
        effective = 0
        # Primary miners
        round = 1
        while workers > 0:
            for base in range(self.bases):
                at_base = min(10, workers)
                effective += at_base / round
                workers -= at_base
            round += 1
        return effective

    def get_bases(self):
        return int(self.units[unit_repo.get_base(self.race).id])

    def get_gas_geysers(self):
        return self.units[unit_repo.get_geyser(self.race).id]

    def get_workers(self):
        return self.units[unit_repo.get_worker(self.race).id]

    def get_supply(self):
        supply = 0
        for unit in unit_repo.units_by_race(self.race):
            supply += unit.supply * self.units[unit.id]
        return supply

    def get_max_supply(self):
        supply = 0
        for building in unit_repo.get_suppliers(self.race):
            if building.name == "Supply Depot" or building.name == "Pylon":
                supply += 8 * self.units[building.id]
            if building.name == "Nexus" or building.name == "Command Center":
                supply += 9 * self.units[building.id]
        return supply

    def has_unit(self, unit):
        if unit.type == Type.UNIT or unit.type == Type.UNIT:
            return self.units[unit.id] > 0
        if unit.type == Type.TECH:
            return self.techs[unit.id] > 0
        if unit.type == Type.UPGRADE:
            return self.upgrades[unit.id] > 0
        return False

    def print(self, opponent=False):
        for i in range(len(self.units)):
            if self.units[i] > 0:
                unit = unit_repo.get_by_id(i)
                print(unit.name + ":" + str(int(self.units[i])))
        for i in range(len(self.techs)):
            if self.techs[i] > 0:
                unit = unit_repo.get_by_id_and_type(i, Type.TECH)
                print(unit.name + ":" + str(int(self.techs[i])))
        for i in range(len(self.upgrades)):
            if self.upgrades[i] > 0:
                unit = unit_repo.get_by_id_and_type(i, Type.UPGRADE)
                print(unit.name + ":" + str(int(self.upgrades[i])))
        for product in self.under_production:
            if not product.done:
                print(product.type.name + " done in " + str((self.frame - product.done_at)))
        if opponent:
            for i in range(len(self.opp_units)):
                if self.opp_units[i] > 0:
                    print(unit_repo.get_by_id(i).name + ":" + str(int(self.opp_units[i])))


class ForwardModel:

    def __init__(self, frames_per_build=300, verbose=False):
        self.verbose = verbose
        self.frames_per_build = frames_per_build

    def random_build(self, race, banned_builds):
        build = random.sample(unit_repo.all_by_race(race), 1)[0]
        while build.name in banned_builds:
            build = random.sample(unit_repo.all_by_race(race), 1)[0]
        return build

    def random_build_order(self, race, time, banned_builds=[]):
        steps = int(time / self.frames_per_build)
        build_order = []

        for i in range(steps):
            build = self.random_build(race, banned_builds)
            build_order.append(build)

        return build_order

    def legal_build_order(self, gamestate, time, banned_builds=[], restricted=[]):
        steps = int(time / self.frames_per_build)

        build_order = []

        # Create gamestate object
        while len(build_order) < steps:
            legal = []
            frame = []
            for unit in unit_repo.all_by_race(gamestate.race):
                if gamestate.units[unit.id] > 0 and unit.name in restricted:
                    continue
                if unit.name not in banned_builds:
                    try:
                        next_frame = gamestate.time_to_produce(unit)
                        legal.append(unit)
                        frame.append(next_frame)
                    except StarCraftException as e:
                        #print(e)
                        continue
            r = int(random.random() * len(legal))
            try:
                gamestate.progress(frame[r])
                gamestate.build(legal[r])
                build_order.append(legal[r])
            except Exception as e:
                # Ignore build
                #print("Build ignored " + ": " + str(e))
                continue
        return build_order

    def run(self, gamestate, build_order, to_frame, force=False):
        # Go through build one at a time
        i = 0
        for build in build_order:

            try:
                next_frame = gamestate.time_to_produce(build, force=force)
                if next_frame <= to_frame:
                    gamestate.progress(next_frame)
                    gamestate.build(build)
                else:
                    gamestate.progress(to_frame)
                    break
            except StarCraftException as e:
                # Skipping build
                if self.verbose:
                    print("Skipping build: {0}".format(e))
            i += 1
        # Progress to all units done or time is up
        if gamestate.frame < to_frame:
            gamestate.progress(to_frame)

        return gamestate, i

    def trim(self, gamestate, build_order, to_frame):

        # Trimmed build order
        trimmed = []

        # Go through build one at a time
        for build in build_order:

            try:
                next_frame = gamestate.time_to_produce(build)
                if next_frame <= to_frame:
                    gamestate.progress(next_frame)
                    gamestate.build(build)
                else:
                    gamestate.progress(to_frame)
                    break
                trimmed.append(build)
            except StarCraftException as e:
                # Skipping build
                i = 0
                if self.verbose:
                    print("Skipping build: {0}".format(e))

        return trimmed
