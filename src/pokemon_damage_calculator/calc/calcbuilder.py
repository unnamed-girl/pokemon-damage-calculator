from pokemon_damage_calculator.calc.damage_calc import damage_calc
from pokemon_damage_calculator.calc.pokemon import (
    IntoPokemon,
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


class Field:
    def __init__(self) -> None:
        self.weather: Weather = Weather.NONE
        self.terrain: Terrain = Terrain.NONE


class GameState:
    def __init__(
        self, format: Format, attacker: IntoPokemon, defender: IntoPokemon
    ) -> None:
        attacker = into_pokemon(attacker)
        defender = into_pokemon(defender)

        self.field = Field()

        self.format = format
        self.attacker = attacker
        self.defender = defender

        queue = SpeedQueue([attacker, defender])
        while p := queue.next():
            enters_effects(p, self.field)

    def switch_attacker(self, attacker: IntoPokemon) -> "GameState":
        self.attacker = into_pokemon(attacker)
        return self

    def switch_defender(self, defender: IntoPokemon) -> "GameState":
        self.defender = into_pokemon(defender)
        return self

    def calc(self, move: IntoMove) -> list[int]:
        return damage_calc(
            self.format, self.field, self.attacker, self.defender, into_move(move)
        )
