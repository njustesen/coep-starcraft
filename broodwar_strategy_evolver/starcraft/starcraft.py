from enum import Enum
import numpy as np


class StarCraftException(Exception):
    pass


class Race(Enum):
    ZERG = 0
    TERRAN = 1
    PROTOSS = 2
    NEUTRAL = 3


class Type(Enum):
    UNIT = 0
    BUILDING = 1
    UPGRADE = 2
    TECH = 3


class UnitType:
    def __init__(self, id, name, type, minerals=0, gas=0, supply=0, build_at=-1, build_time=0, requires=[]):
        self.id = id
        self.name = name
        self.minerals = minerals
        self.gas = gas
        self.supply = supply
        self.build_at = build_at
        self.build_time = build_time
        self.requires = set(requires)
        self.type = type


class Unit:
    def __init__(self, id, type_id, idx=-1):
        self.id = id
        self.idx = idx
        self.type_id = type_id


class UnitEvent:
    def __init__(self, frame, unit_id, unit_type, event_type, race=Race.PROTOSS):
        self.frame = frame
        self.race = race
        self.unit_id = unit_id
        self.unit_type = unit_type
        self.event_type = event_type


class ResearchEvent:
    def __init__(self, frame, race, type):
        self.frame = frame
        self.race = race
        self.type = type


class Frame:
    def __init__(self, frame_num, own_units, opp_units):
        self.frame_num = frame_num
        self.own_units = own_units
        self.own_units = own_units


class Game:
    def __init__(self, replay_id, winner_race, looser_race, duration):
        self.replay_id = replay_id
        self.winner_race = winner_race
        self.looser_race = looser_race
        self.duration = duration
        self.frames = []
