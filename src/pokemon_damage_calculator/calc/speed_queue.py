from typing import Iterable, Optional

from pokemon_damage_calculator.calc.pokemon import Pokemon
from pokemon_damage_calculator.model.enums import Stat


class SpeedQueue:
    def __init__(self, pokemon: Optional[Iterable[Pokemon]] = None) -> None:
        self.queue = list(pokemon) if pokemon else []

    def next(self) -> Optional[Pokemon]:
        if len(self.queue) == 0:
            return None
        self.queue.sort(key=lambda pokemon: pokemon.stat(Stat.Speed))
        return self.queue.pop()
