import functools
import json
from typing import List

from managers.process_memory_manager import Process

with open('memory_settings.json', 'r') as f:
    config = json.load(f)


class Liquid:
    TYPES = ['water', 'chocolate', 'lava', 'plasma']

    def __init__(self, trove: Process, name: str, caught_fish_offsets: List, pole_in_liquid_offsets: List):
        self.trove = trove
        self.name = name

        self.base_address = self.trove.base_address + int(config['base'], 16)

        self.caught_fish_offsets = caught_fish_offsets
        self.pole_in_liquid_offsets = pole_in_liquid_offsets

    @functools.cached_property
    def caught_fish_pointer(self):
        return self.trove.read_memory(self.base_address, self.caught_fish_offsets)[0]

    @functools.cached_property
    def pole_in_liquid_pointer(self):
        return self.trove.read_memory(self.base_address, self.pole_in_liquid_offsets)[0]

    @property
    def caught_fish(self) -> bool:
        _, _caught_fish = self.trove.read_memory(self.caught_fish_pointer, None)

        return _caught_fish == 1

    @property
    def pole_in_liquid(self) -> bool:
        _, _pole_in_liquid = self.trove.read_memory(self.pole_in_liquid_pointer, None)

        return _pole_in_liquid == 1

    @classmethod
    def get_all(cls, trove: Process) -> List["Liquid"]:
        ret = []
        for liquid_type in Liquid.TYPES:
            ret.append(cls(trove, name=liquid_type,
                           caught_fish_offsets=config['caught_fish_offsets'][liquid_type],
                           pole_in_liquid_offsets=config['pole_in_liquid_offsets'][liquid_type]))
        return ret

    def __str__(self):
        return self.name.title()
