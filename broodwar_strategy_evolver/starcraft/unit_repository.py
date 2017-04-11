from . import starcraft as sc
import os

path = os.path.dirname(os.path.realpath(__file__))


class UnitRepository:

    def __init__(self):
        self.units_by_id = {}
        self.all_by_name = {}
        self.protoss_by_id = {}
        self.terran_by_id = {}
        self.zerg_by_id = {}
        self.units = self.load_all_unit_types(path+"/data/all_units.csv")
        self.terran = self.load_unit_types(path+"/data/terran_unit_types.csv", "terran")
        self.protoss = self.load_unit_types(path+"/data/protoss_unit_types.csv", "protoss")
        self.zerg = self.load_unit_types(path+"/data/zerg_unit_types.csv", "zerg")
        self.techs_by_id = {}
        self.upgrades_by_id = {}
        self.techs = self.load_techs_upgrades(path+"/data/sc_tech.csv", sc.Type.TECH)
        self.upgrades = self.load_techs_upgrades(path+"/data/sc_upgrades.csv", sc.Type.UPGRADE)
        self.terran_tech = []
        self.protoss_tech = []
        self.zerg_tech = []
        self.terran_upgrades = []
        self.protoss_upgrades = []
        self.zerg_upgrades = []
        self.split_techs()
        self.all_terran = self.terran + self.terran_tech + self.terran_upgrades
        self.all_protoss = self.protoss + self.protoss_tech + self.protoss_upgrades
        self.all_zerg = self.zerg + self.zerg_tech + self.zerg_upgrades
        self.set_indices()

    def set_indices(self):
        i = 0
        for unit in self.terran:
            unit.idx = i
            self.all_by_name[unit.name].idx = i
            #self.units_by_id[unit.id].idx = i
            i += 1
        for tech in self.terran_tech:
            tech.idx = i
            self.all_by_name[tech.name].idx = i
            i += 1
        for upgrade in self.terran_upgrades:
            upgrade.idx = i
            self.all_by_name[upgrade.name].idx = i
            i += 1

        i = 0
        for unit in self.protoss:
            unit.idx = i
            self.all_by_name[unit.name].idx = i
            i += 1
        for tech in self.protoss_tech:
            tech.idx = i
            self.all_by_name[tech.name].idx = i
            i += 1
        for upgrade in self.protoss_upgrades:
            upgrade.idx = i
            self.all_by_name[upgrade.name].idx = i
            i += 1

    def split_techs(self):
        for tech in self.techs:
            if tech.build_at in self.terran_by_id:
                self.terran_tech.append(tech)
            elif tech.build_at in self.protoss_by_id:
                self.protoss_tech.append(tech)
            elif tech.build_at in self.zerg_by_id:
                self.zerg_tech.append(tech)
        for upgrade in self.upgrades:
            if upgrade.build_at in self.terran_by_id:
                self.terran_upgrades.append(upgrade)
            elif upgrade.build_at in self.protoss_by_id:
                self.protoss_upgrades.append(upgrade)
            elif upgrade.build_at in self.zerg_by_id:
                self.zerg_upgrades.append(upgrade)

    def load_techs_upgrades(self, filename, type):
        techs = []
        file = open(filename, 'r')
        idx = 0
        for line in file:
            if idx == 0:
                idx += 1
                continue

            attributes = line.split('\n')[0].split(';')
            type_id = idx - 1
            name = attributes[0]
            minerals = 0
            gas = 0
            time = 0
            researched_at = -1

            # Known index?
            if name != "---" and attributes[1] != "":
                minerals = int(attributes[1])
                gas = int(attributes[2])
                time = int(attributes[3])
                researched_at = int(attributes[4])

            tech = sc.UnitType(type_id, name=name, type=type, minerals=minerals, gas=gas, build_at=researched_at, build_time=time)
            techs.append(tech)
            self.all_by_name[tech.name] = tech
            if type == sc.Type.TECH:
                self.techs_by_id[tech.id] = tech
            elif type == sc.Type.UPGRADE:
                self.upgrades_by_id[tech.id] = tech
            idx += 1

        return techs

    def load_unit_types(self, filename, race):
        units = []
        file = open(filename, 'r')
        idx = 0
        for line in file:
            if idx == 0:
                idx += 1
                continue

            attributes = line.split('\n')[0].split(';')
            type_id = int(attributes[0])
            name = attributes[1]
            type = sc.Type.UNIT
            if attributes[2] == "building":
                type = sc.Type.BUILDING

            minerals = attributes[3]
            try:
                minerals = int(minerals)
                minerals = float(minerals)
            except Exception as e:
                print(minerals)
                minerals = float(minerals)
            gas = int(attributes[4])
            sup = float(attributes[5])

            if attributes[6] == "":
                build_at = -1   # Is build by worker
                build_time = int(attributes[7])
            elif attributes[6] == "-":
                build_at = -2   # Cannot be build
                build_time = 0
            else:
                build_at = int(attributes[6])
                build_time = int(attributes[7])

            requires_str = attributes[8].split(",")
            requires = []
            for i in range(len(requires_str)):
                if requires_str[i] not in ["\n", "\r", ""]:
                    requires.append(int(requires_str[i]))

            unit_type = sc.UnitType(type_id, name, type=type, minerals=minerals, gas=gas, supply=sup, build_at=build_at, build_time=build_time, requires=requires)
            self.units_by_id[unit_type.id] = unit_type
            self.all_by_name[unit_type.name] = unit_type
            if race == "terran":
                self.terran_by_id[unit_type.id] = unit_type
            elif race == "protoss":
                self.protoss_by_id[unit_type.id] = unit_type
            elif race == "zerg":
                self.zerg_by_id[unit_type.id] = unit_type
            units.append(unit_type)
            idx += 1
        return units

    def load_all_unit_types(self, file_name):
        units = []
        file = open(file_name, 'r')
        idx = 0
        for line in file:
            type_id = idx
            attributes = line.split('\n')[0]
            name = attributes.split(';')[0]

            if type_id == 30:   # Treat sieged tanks as normal tanks
                type_id = 5

            unit_type = sc.UnitType(type_id, name, type=sc.Type.UNIT)   # Treat as unit for now
            units.append(unit_type)
            idx += 1
        return units

    def get_race(self, id):
        if id in self.terran_by_id:
            return sc.Race.TERRAN
        elif id in self.protoss_by_id:
            return sc.Race.PROTOSS
        elif id in self.zerg_by_id:
            return sc.Race.ZERG
        return sc.Race.NEUTRAL

    def has_unit_id(self, id):
        return id in self.units_by_id

    def get_by_id(self, id):
        '''
        Only returns buildings and units
        '''
        if id < 0:
            return None
        return self.units_by_id[id]

    def get_by_id_and_type(self, id, type):
        '''
        Can also return tech and upgrades
        '''
        if type == sc.Type.UNIT or type == sc.Type.BUILDING:
            return self.units_by_id[id]
        elif type == sc.Type.TECH:
            return self.techs_by_id[id]
        elif type == sc.Type.UPGRADE:
            return self.upgrades_by_id[id]

    def get_by_name(self, name):
        return self.all_by_name[name]

    def get_by_idx(self, idx):
        if idx >= len(self.protoss):
            return self.terran[idx - len(self.protoss)]
        return self.protoss[idx]

    def get_by_race_idx(self, idx, race):
        if race == sc.Race.PROTOSS:
            if idx < len(self.protoss):
                return self.protoss[idx]
            elif idx < len(self.protoss) + len(self.protoss_tech):
                return self.protoss_tech[idx - len(self.protoss)]
            elif idx < len(self.protoss) + len(self.protoss_tech) + len(self.protoss_upgrades):
                return self.protoss_upgrades[idx - len(self.protoss) - len(self.protoss_tech)]
        elif race == sc.Race.TERRAN:
            if idx < len(self.terran):
                return self.terran[idx]
            elif idx < len(self.terran) + len(self.terran_tech):
                return self.terran_tech[idx - len(self.terran)]
            elif idx < len(self.terran) + len(self.terran_tech) + len(self.terran_upgrades):
                return self.terran_upgrades[idx - len(self.terran) - len(self.terran_tech)]
        raise sc.StarCraftException("Unknown unit index or race")

    def get_idx_by_name(self, race_a, race_b, name):
        idx = 0
        for type in self.units_by_race(race_a):
            if type.name == name:
               return idx + len(self.units_by_race(race_b))
            idx += 1

    def units_by_race(self, race):
        if race == sc.Race.TERRAN:
            return self.terran
        elif race == sc.Race.PROTOSS:
            return self.protoss
        elif race == sc.Race.ZERG:
            return self.zerg

        raise Exception("Unknown race")

    def techs_by_race(self, race):
        if race == sc.Race.TERRAN:
            return self.terran_tech
        elif race == sc.Race.PROTOSS:
            return self.protoss_tech
        elif race == sc.Race.ZERG:
            return self.zerg_tech

        raise Exception("Unknown race")

    def all_by_race(self, race):
        if race == sc.Race.TERRAN:
            return self.all_terran
        elif race == sc.Race.PROTOSS:
            return self.all_protoss
        elif race == sc.Race.ZERG:
            return self.all_zerg

        raise Exception("Unknown race")


    def upgrades_by_race(self, race):
        if race == sc.Race.TERRAN:
            return self.terran_upgrades
        elif race == sc.Race.PROTOSS:
            return self.protoss_upgrades
        elif race == sc.Race.ZERG:
            return self.zerg_upgrades

        raise Exception("Unknown race")

    def get_base(self, race):
        #TODO: Expand to also contain lair and hive
        if race == sc.Race.PROTOSS:
            return self.get_by_name("Nexus")
        elif race == sc.Race.TERRAN:
            return self.get_by_name("Command Center")
        elif race == sc.Race.ZERG:
            return self.get_by_name("Hatchery")
        raise Exception("Unknown race")

    def get_worker(self, race):
        if race == sc.Race.PROTOSS:
            return self.get_by_name("Probe")
        elif race == sc.Race.TERRAN:
            return self.get_by_name("SCV")
        elif race == sc.Race.ZERG:
            return self.get_by_name("Drone")
        raise Exception("Unknown race")

    def get_suppliers(self, race):
        if race == sc.Race.PROTOSS:
            return [self.get_by_name("Nexus"), self.get_by_name("Pylon")]
        elif race == sc.Race.TERRAN:
            return [self.get_by_name("Command Center"), self.get_by_name("Supply Depot")]
        elif race == sc.Race.ZERG:
            return [self.get_by_name("Hatchery"), self.get_by_name("Lair"), self.get_by_name("Hive"), self.get_by_name("Overlord")]
        raise Exception("Unknown race")

    def get_geyser(self, race):
        if race == sc.Race.PROTOSS:
            return self.get_by_name("Assimilator")
        elif race == sc.Race.TERRAN:
            return self.get_by_name("Refinery")

#table = UnitTable()
#print("Unit table loaded")
