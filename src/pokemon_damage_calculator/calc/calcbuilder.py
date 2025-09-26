from pokemon_damage_calculator.calc.damage_calc import damage_calc
from pokemon_damage_calculator.calc.pokemon import Pokemon
from pokemon_damage_calculator.data import get_move
from pokemon_damage_calculator.model.models import Move


class CalcBuilder:
    def __init__(self, doubles: bool) -> None:
        self.doubles = doubles
        self.move = None

    @staticmethod
    def gen9vgc() -> "CalcBuilder":
        return CalcBuilder(True)

    def calc(self, attacker: Pokemon, defender: Pokemon, move: Move | str) -> list[int]:
        if type(move) == str:
            move = get_move(move)
        elif type(move) == Move:
            pass
        else:
            assert False
        return damage_calc(move, attacker, defender)
