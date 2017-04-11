import numpy as np
import random
from enum import Enum
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.starcraft.starcraft import Race, Type
from broodwar_strategy_evolver.starcraft.forward_model import ForwardModel, GameState
from broodwar_strategy_evolver.starcraft.adv_heuristics import heuristic

unit_repo = UnitRepository()
banned_builds = ["Shuttle", "Shield Battery"]
restricted_builds = ["Forge", "Cybernetics Core", "Observer", "Fleet Beacon", "Citadel of Adun", "Templar Archives", "Robotics Support Bay"]


class CrossoverMethod(Enum):
    UNIFORM = 1
    SINGLE_POINT = 2
    TWO_POINT = 3


class Genome:

    def __init__(self, protected=False):
        self.gamestate = None
        self.build_order = []
        self.fitness = 0
        self.protected = protected


class Evolution:

    def __init__(self,
                 gamestate,
                 pop_size=64,
                 horizon=24*60*4,
                 survival_rate=0.5,
                 bellman=0,
                 crossover_method=CrossoverMethod.UNIFORM,
                 frames_per_build=300,
                 discount=0.9,
                 basic_add_mutate_prob=0.0,
                 add_mutate_prob=0.5,
                 remove_mutate_prob=0.5,
                 swap_mutate_prob=0.5,
                 clone_mutate_prob=0.5,
                 chain_mutate_prob=0.0,
                 random_fitness=False):

        # State
        self.gamestate = gamestate

        # If no observations - populate with starting state - requires race to be set
        if len(self.gamestate.units) == 0:
            self.gamestate.units = np.zeros(len(unit_repo.units))
            self.gamestate.units[unit_repo.get_worker(gamestate.race).id] = 10
            self.gamestate.units[unit_repo.get_base(gamestate.race).id] = 1
        if len(self.gamestate.opp_units) == 0:
            self.gamestate.opp_units = np.zeros(len(unit_repo.units))
            self.gamestate.opp_units[unit_repo.get_worker(gamestate.opp_race).id] = 10
            self.gamestate.opp_units[unit_repo.get_base(gamestate.opp_race).id] = 1
        if len(self.gamestate.techs) == 0:
            self.gamestate.techs = np.zeros(len(unit_repo.techs))
        if len(self.gamestate.upgrades) == 0:
            self.gamestate.upgrades = np.zeros(len(unit_repo.upgrades))

        # Evolution
        self.random_fitness = random_fitness
        self.basic_add_mutate_prob = basic_add_mutate_prob
        self.add_mutate_prob = add_mutate_prob
        self.remove_mutate_prob = remove_mutate_prob
        self.clone_mutate_prob = clone_mutate_prob
        self.swap_mutate_prob = swap_mutate_prob
        self.chain_mutate_prob = chain_mutate_prob
        self.frames_per_build = frames_per_build
        self.discount = discount
        self.horizon = horizon
        self.bellman = bellman
        self.pop_size = pop_size
        self.survival_rate = survival_rate
        self.crossover_method = crossover_method
        self.genomes = []

        # Init population
        self.forward_model = ForwardModel(frames_per_build=self.frames_per_build)
        for i in range(pop_size):
            genome = self.new_genome()
            self.genomes.append(genome)

        # Sort by fitness
        self.genomes.sort(key=lambda x: x.fitness, reverse=True)

    def get_fitness(self):
        return self.genomes[0].fitness

    def init_genome(self, genome, bellman=0):
        step_size = self.horizon
        steps_taken = 0
        if bellman > 0:
            step_size = int(min(self.horizon, bellman*24*60))
        genome.fitness = 0
        build_order = list(genome.build_order)
        genome.gamestate = self.gamestate.clone()
        start = genome.gamestate.frame
        build_idx = 0
        last_fitness = 0
        while genome.gamestate.frame < start + self.horizon:
            time = min(start + self.horizon, genome.gamestate.frame + step_size)
            # If builds left - build it
            if build_idx < len(genome.build_order):
                genome.gamestate, idx = self.forward_model.run(genome.gamestate,
                                                                build_order=build_order[build_idx:],
                                                                to_frame=time)
                build_idx += idx
                last_fitness = self.fitness(genome)
            else:
                genome.gamestate.progress(time)

            # Add to fitness - if no step then add last fitness
            if genome.gamestate.frame > 4 * 24 * 60:
                genome.fitness += last_fitness * (self.discount**steps_taken)  # Bellman
                steps_taken += 1

        if steps_taken == 0:
            genome.fitness += self.fitness(genome) * (self.discount**steps_taken)
            steps_taken += 1

    def new_genome(self, build_order=None, run=True):
        genome = Genome()
        if build_order is not None:
            genome.build_order = list(build_order)
        else:
            genome.build_order = self.forward_model.legal_build_order(self.gamestate.clone(),
                                                                 self.horizon,
                                                                 banned_builds=banned_builds,
                                                                 restricted=restricted_builds)
        if run:
            self.init_genome(genome, bellman=self.bellman)
        return genome

    def fitness(self, genome):
        if self.random_fitness:
            return random.random()
        return heuristic(genome.gamestate, banned_builds, restricted_builds)

    def update(self):

        # Survival
        self.reduce(int(self.pop_size * self.survival_rate))

        # Crossover
        children_own = self.reproduce(self.pop_size, self.crossover_method)

        # Mutation
        self.mutate_pop(children_own)

        # Run genomes to set fitness
        for genome in children_own:
            self.init_genome(genome, bellman=self.bellman)

        # Extend populations with offspring
        self.genomes.extend(children_own)

        # Sort by fitness
        self.genomes.sort(key=lambda x: x.fitness, reverse=True)

    def combine_units(self, a, a_race, b, b_race):
        combined = np.zeros(len(a) + len(b))
        a_units = unit_repo.units_by_race(a_race)
        for type in a_units:
            combined[type.id] = a[type.id]
        b_units = unit_repo.units_by_race(b_race)
        for type in b_units:
            combined[type.id] = b[type.id]
        return combined

    def get_build_order(self, trimmed=False):

        if trimmed:
            # Create clone of gamestate object
            clone = self.gamestate.clone()
            build_order = self.forward_model.trim(clone, self.genomes[0].build_order, to_frame=clone.frame + self.horizon)
        else:
            build_order = self.genomes[0].build_order
        return build_order

    def units_build(self, a, b):
        builds = []
        for i in range(len(a)):
            if b[i] > a[i]:
                for n in range(int(b[i]) - int(a[i])):
                    builds.append(i)
        return builds

    def remove_build(self, unit):
        for genome in self.genomes:
            # Remove first instance of build
            idx = 0
            for build in genome.build_order:
                if build.id == unit.id and build.type == unit.type:
                    del genome.build_order[idx]
                    # Add build to end
                    genome.build_order.append(build)
                    break
                idx += 1
            self.init_genome(genome)

    def combine(self, completed, under_construction):
        all = np.zeros(len(completed))
        for i in range(len(completed)):
            all[i] = completed[i]
            for construction in under_construction[i]:
                all[i] += 1
        return all

    def update_state(self, gamestate):

        # Collect completed and under construction
        all_units_before = self.combine(self.gamestate.units, self.gamestate.units_under_construction)
        all_units_after = self.combine(gamestate.units, gamestate.units_under_construction)
        all_techs_before = self.combine(self.gamestate.techs, self.gamestate.techs_under_construction)
        all_techs_after = self.combine(gamestate.techs, gamestate.techs_under_construction)
        all_upgrades_before = self.combine(self.gamestate.upgrades, self.gamestate.upgrades_under_construction)
        all_upgrades_after = self.combine(gamestate.upgrades, gamestate.upgrades_under_construction)

        # Update build orders
        for unit in self.units_build(all_units_before, all_units_after):
            self.remove_build(unit_repo.get_by_id(unit))
        for tech in self.units_build(all_techs_before, all_techs_after):
            self.remove_build(unit_repo.get_by_id_and_type(tech, Type.TECH))
        for upgrade in self.units_build(all_upgrades_before, all_upgrades_after):
            self.remove_build(unit_repo.get_by_id_and_type(upgrade, Type.UPGRADE))

        # Update state
        self.gamestate = gamestate.clone()

    def reduce(self, size):
        self.genomes = self.genomes[:size]

    def reproduce(self, size, method):
        children = []
        child_a = None
        child_b = None
        while len(self.genomes) + len(children) < size:
            parents = random.sample(self.genomes, 2)
            # Do not crossover protected genomes
            while parents[0].protected or parents[1].protected:
                parents = random.sample(self.genomes, 2)
            if method == CrossoverMethod.UNIFORM:
                child_a = self.uniform_crossover(parents[0], parents[1])
            elif method == CrossoverMethod.SINGLE_POINT:
                child_a, child_b = self.n_point_crossover(parents[0], parents[1], 1)
            elif method == CrossoverMethod.TWO_POINT:
                child_a, child_b = self.n_point_crossover(parents[0], parents[1], 2)
            children.append(child_a)
            if child_b is not None and len(self.genomes) + len(children) < size:
                children.append(child_b)
        return children

    def n_point_crossover(self, parent_a, parent_b, n):
        build_order_a = []
        build_order_b = []
        if len(parent_a.build_order) != len(parent_b.build_order):
            raise Exception("Different lengths of build orders: " + str(len(parent_a.build_order)) + " - " + str(len(parent_b.build_order)))

        # Create split points
        points = []
        for p in range(n):
            points.append(random.random() * len(parent_a.build_order))

        a = True
        point_idx = 0
        for i in range(max(len(parent_a.build_order), len(parent_b.build_order))):
            # Next point reached?
            if i >= points[point_idx]:
                a = not a
                if point_idx + 1 < len(points):
                    point_idx += 1
            # Add build from parent
            if a:
                build_order_a.append(parent_a.build_order[i])
                build_order_b.append(parent_b.build_order[i])
            else:
                build_order_a.append(parent_b.build_order[i])
                build_order_b.append(parent_a.build_order[i])
        offspring_a = self.new_genome(build_order=build_order_a, run=False)
        offspring_b = self.new_genome(build_order=build_order_b, run=False)

        return offspring_a, offspring_b

    def uniform_crossover(self, parent_a, parent_b):
        build_order = []
        if len(parent_a.build_order) != len(parent_b.build_order):
            raise Exception("Different lengths of build orders")
        for i in range(max(len(parent_a.build_order), len(parent_b.build_order))):
            if random.random() >= 0.5:
                build_order.append(parent_a.build_order[i])
            else:
                build_order.append(parent_b.build_order[i])

        offspring = self.new_genome(build_order=build_order, run=False)

        return offspring

    def mutate_pop(self, genomes_to_mutate):
        for genome in genomes_to_mutate:
            if random.random() <= self.basic_add_mutate_prob:
                self.add_mutate(genome, True)
            if random.random() <= self.add_mutate_prob:
                self.add_mutate(genome, False)
            if random.random() <= self.swap_mutate_prob:
                self.swap_mutate(genome)
            if random.random() <= self.clone_mutate_prob:
                self.clone_mutate(genome)
            if random.random() <= self.remove_mutate_prob:
                self.remove_mutate(genome)
            if random.random() <= self.chain_mutate_prob:
                self.chain_mutate(genome)

    def remove_mutate(self, genome):
        idx = int(random.random() * len(genome.build_order)) - 1
        new_build = self.forward_model.random_build(self.gamestate.race, banned_builds)
        genome.build_order = genome.build_order[:idx] + genome.build_order[idx:len(genome.build_order)-1] + [new_build]

    def build_before(self, build, build_order, idx):
        i = 0
        for b in build_order:
            if i >= idx:
                break
            if b.id == build.id and b.type == build.type:
                return True
            i += 0
        if self.gamestate.has_unit(build):
            return True
        return False

    def recursive_requirements(self, build):
        reqs = []
        build_reqs = set(build.requires)
        if build.build_at >= 0:
            build_reqs.add(build.build_at)
        for r in build_reqs:
            req = unit_repo.get_by_id(r)
            for rec_req in self.recursive_requirements(req):
                if rec_req not in reqs:
                    reqs.append(rec_req)
            if req not in reqs:
                reqs.append(req)
        return reqs

    def add_mutate(self, genome, basic):
        idx = int(random.random() * len(genome.build_order))
        new_build = self.forward_model.random_build(self.gamestate.race, banned_builds)
        if basic:
            genome.build_order = genome.build_order[:idx] + [new_build] + genome.build_order[idx:len(genome.build_order)-1]
            return genome
        requirements = self.recursive_requirements(new_build)
        for req in requirements:
            if not self.build_before(req, genome.build_order, idx):
                if idx + 1 < len(genome.build_order):
                    genome.build_order = genome.build_order[:idx] + [req] + genome.build_order[idx:len(genome.build_order)-1]
                    idx += 1
                    if req.name == "High Templar" and idx + 1 < len(genome.build_order):
                        genome.build_order = genome.build_order[:idx] + [req] + genome.build_order[idx:len(genome.build_order)-1]
                        idx += 1
        if idx + 1 < len(genome.build_order):
            genome.build_order = genome.build_order[:idx] + [new_build] + genome.build_order[idx:len(genome.build_order)-1]
        return genome

    def chain_mutate(self, genome):
        idx_a = int(random.random() * len(genome.build_order) - 1)
        while idx_a + 2 < len(genome.build_order):
            idx_b = idx_a + 1
            build_a = genome.build_order[idx_a]
            units = []
            for unit in unit_repo.all_by_race(self.gamestate.race):
                if build_a.id in unit.requires:
                    units.append(unit)
            if len(units) > 0:
                build_b = random.sample(units, 1)[0]
                genome.build_order[idx_a] = build_a
                genome.build_order[idx_b] = build_b
            else:
                break
            idx_a = idx_b
        return genome

    def swap_mutate(self, genome):
        idx_a = int(random.random() * len(genome.build_order))
        idx_b = int(random.random() * len(genome.build_order))
        build_a = genome.build_order[idx_a]
        build_b = genome.build_order[idx_b]
        genome.build_order[idx_a] = build_b
        genome.build_order[idx_b] = build_a
        return genome

    def clone_mutate(self, genome):
        idx_a = int(random.random() * len(genome.build_order))
        idx_b = int(random.random() * len(genome.build_order))
        build_a = genome.build_order[idx_a]
        genome.build_order[idx_b] = build_a
        return genome

