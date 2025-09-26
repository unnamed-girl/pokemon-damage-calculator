from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.model.enums import Stat
from pokemon_damage_calculator.model.natures import Nature


def flareon():
    return (
        PokemonBuilder("flareon")
        .ev(Stat.Defence, 99)
        .ev(Stat.SpecialDefence, 99)
        .nature(Nature.BOLD)
        .build()
    )
