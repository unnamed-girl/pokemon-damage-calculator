from pokemon_damage_calculator.calc.calcbuilder import CalcBuilder
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.model.enums import Ability, Stat
from pokemon_damage_calculator.model.natures import Nature
from test.testutils import flareon


# def test_parental_bond_boost():
#     first_hit = [100, 101, 102, 103, 105, 106, 107, 108, 109, 110, 112, 113, 114, 115, 116, 118]
#     second_hit = [37, 37, 38, 38, 39, 39, 40, 40, 40, 41, 41, 42, 42, 43, 43, 44]
#     total = [first_hit[i] + second_hit[i] for i in range(len(first_hit))]

#     assert CalcBuilder.gen9vgc().calc(
#         (
#             PokemonBuilder("kangaskhanmega")
#             .ev(Stat.Attack, 252)
#             .nature(Nature.JOLLY)
#             .level(100)
#             .ability(Ability.ParentalBond)
#             .build()
#         ),
#         flareon(),
#         "poweruppunch",
#     ) == total


def test_parental_bond_damage():
    first_hit = [
        174,
        176,
        178,
        180,
        182,
        184,
        186,
        188,
        190,
        192,
        194,
        196,
        198,
        200,
        202,
        205,
    ]
    second_hit = [43, 43, 44, 44, 45, 45, 46, 46, 47, 47, 48, 48, 49, 49, 50, 51]
    total = [first_hit[i] + second_hit[i] for i in range(len(first_hit))]

    assert (
        CalcBuilder.gen9vgc().calc(
            (
                PokemonBuilder("kangaskhanmega")
                .ev(Stat.Attack, 252)
                .nature(Nature.JOLLY)
                .level(100)
                .ability(Ability.ParentalBond)
                .build()
            ),
            flareon(),
            "suckerpunch",
        )
        == total
    )
