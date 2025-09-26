from pokemon_damage_calculator.calc.calcbuilder import Format, IntoMove, IntoPokemon
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.model.enums import Stat
from pokemon_damage_calculator.model.natures import Nature


def standard_calc(
    format: Format, attacker: IntoPokemon, defender: IntoPokemon, move: IntoMove
) -> list[int]:
    return format.game(attacker, defender).calc(move)


def flareon():
    return (
        PokemonBuilder("flareon")
        .ev(Stat.Defence, 99)
        .ev(Stat.SpecialDefence, 99)
        .nature(Nature.BOLD)
        .build()
    )
