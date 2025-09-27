from typing import Iterable, Optional, TYPE_CHECKING

from pokemon_damage_calculator.calc.pokemon import Pokemon
from pokemon_damage_calculator.model.enums import Stat

if TYPE_CHECKING:
    from pokemon_damage_calculator.calc.calcbuilder import GameState


class SpeedQueue:
    def __init__(self, pokemon: Optional[Iterable[Pokemon]] = None) -> None:
        self.queue = list(pokemon) if pokemon else []

    def add(self, pokemon: Pokemon) -> None:
        self.queue.append(pokemon)

    def next(self, game_state: "GameState") -> Optional[Pokemon]:
        if len(self.queue) == 0:
            return None
        self.queue.sort(key=lambda pokemon: pokemon.stat(Stat.Speed, game_state))
        return self.queue.pop()
