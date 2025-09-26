from pokemon_damage_calculator.calc.calcbuilder import Format
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.model.enums import Ability
from test.testutils import standard_calc


def test_ignore_wonderguard():
    # Wonderguard standalone
    assert standard_calc(
        Format.gen9vgc(),
        (PokemonBuilder("gyaradosmega")),
        (PokemonBuilder("shedinja").ability(Ability.WonderGuard)),
        "waterfall",
    ) == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # Ignored
    assert standard_calc(
        Format.gen9vgc(),
        (PokemonBuilder("gyaradosmega").ability(Ability.MoldBreaker)),
        (PokemonBuilder("shedinja").ability(Ability.WonderGuard)),
        "waterfall",
    ) == [
        121,
        123,
        124,
        126,
        127,
        129,
        130,
        132,
        133,
        135,
        136,
        138,
        139,
        141,
        142,
        144,
    ]
