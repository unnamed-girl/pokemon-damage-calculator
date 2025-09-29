from typing import Optional
from pokemon_damage_calculator.calc.damage_calc import damage_calc
from pokemon_damage_calculator.calc.pokemon import (
    IntoPokemon,
    Pokemon,
    into_pokemon,
)
from pokemon_damage_calculator.calc.speed_queue import SpeedQueue
from pokemon_damage_calculator.data import IntoMove, into_move
from pokemon_damage_calculator.model.enums import Terrain, Weather
from pokemon_damage_calculator.model.logic import enters_effects


class Format:
    def __init__(self, gen: int, doubles: bool) -> None:
        self.gen = gen
        self.doubles = doubles

    @staticmethod
    def gen9vgc() -> "Format":
        return Format(9, True)

    def game(self, attacker: IntoPokemon, defender: IntoPokemon) -> "GameState":
        return GameState(self, attacker, defender)


class GameState:
    def __init__(
        self,
        format: Format,
        attacker: Optional[IntoPokemon],
        defender: Optional[IntoPokemon],
    ) -> None:
        self.pokemon: list[Pokemon] = []
        queue = SpeedQueue()
        if attacker:
            attacker = into_pokemon(attacker)
            self.attacker = attacker
            queue.add(attacker)
            self.pokemon.append(attacker)
        if defender:
            defender = into_pokemon(defender)
            self.defender = defender
            queue.add(defender)
            self.pokemon.append(defender)

        self.format = format
        self.weather: Weather = Weather.NONE
        self.terrain: Terrain = Terrain.NONE

        while p := queue.next(self):
            enters_effects(p, self)

    def switch_attacker(self, attacker: IntoPokemon) -> "GameState":
        self.attacker = into_pokemon(attacker)
        return self

    def switch_defender(self, defender: IntoPokemon) -> "GameState":
        self.defender = into_pokemon(defender)
        return self

    def calc(self, move: IntoMove) -> list[int]:
        return damage_calc(self, self.attacker, self.defender, into_move(move))
