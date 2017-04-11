import numpy as np
from broodwar_strategy_evolver.starcraft.unit_repository import UnitRepository
from broodwar_strategy_evolver.evolution.stub import Stub

unit_repo = UnitRepository()

stub_build_order = [
    unit_repo.get_by_name("Probe").id,
    unit_repo.get_by_name("Pylon").id,
    unit_repo.get_by_name("Gateway").id,
    unit_repo.get_by_name("Assimilator").id,
    unit_repo.get_by_name("Cybernetics Core").id,
    unit_repo.get_by_name("Dragoon").id,
    unit_repo.get_by_name("Zealot").id
]
stub_units = np.zeros(len(unit_repo.units))
stub_units[unit_repo.get_by_name("Probe").id] = 4
stub_units[unit_repo.get_by_name("Nexus").id] = 1

stub = Stub(stub_build_order, list(stub_units))


def print_current_build_order():
    print("-- Build order:")
    for build in stub.get_build_order():
        print(unit_repo.get_by_id(build).name)
    print("---------------")


def build(name):
    print("-- Building " + name)
    stub_units[unit_repo.get_by_name(name).id] += 1
    stub.update_units(stub_units)
    print("---------------")

print_current_build_order()
build("Probe")
print_current_build_order()
build("Probe")
print_current_build_order()
build("Pylon")
print_current_build_order()
build("Gateway")
print_current_build_order()
build("Assimilator")
print_current_build_order()
build("Cybernetics Core")
print_current_build_order()
build("Dragoon")
print_current_build_order()
build("Zealot")
print_current_build_order()