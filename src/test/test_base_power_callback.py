from pokemon_damage_calculator.calc.calcbuilder import Format
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from test.testutils import standard_calc


def test_low_kick():
    assert standard_calc(
        format=Format.gen9vgc(),
        attacker=PokemonBuilder("swampert").build(),
        defender=PokemonBuilder("swampert").build(),
        move="lowkick",
    ) == [
        36,
        36,
        37,
        37,
        38,
        38,
        39,
        39,
        39,
        40,
        40,
        41,
        41,
        42,
        42,
        43,
    ]

    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("cosmoem"),
        PokemonBuilder("cosmoem"),
        "lowkick",
    ) == [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9]

    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("tyrogue"),
        PokemonBuilder("tyrogue"),
        "lowkick",
    ) == [24, 24, 24, 24, 24, 25, 25, 25, 25, 25, 27, 27, 27, 27, 27, 28]


def test_electro_ball():
    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("electrode").build(),
        PokemonBuilder("tyrogue").build(),
        "electroball",
    ) == [84, 84, 85, 87, 87, 88, 90, 90, 91, 93, 93, 94, 96, 96, 97, 99]

    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("cosmoem").build(),
        PokemonBuilder("electrode").build(),
        "electroball",
    ) == [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5]


def test_heavy_slam():
    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("electrode").build(),
        PokemonBuilder("tyrogue").build(),
        "heavyslam",
    ) == [39, 39, 40, 40, 40, 41, 41, 42, 42, 43, 43, 44, 44, 45, 45, 46]

    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("cosmoem").build(),
        PokemonBuilder("electrode").build(),
        "heavyslam",
    ) == [12, 12, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 15]


def test_heat_crash():
    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("electrode").build(),
        PokemonBuilder("tyrogue").build(),
        "heatcrash",
    ) == [39, 39, 40, 40, 40, 41, 41, 42, 42, 43, 43, 44, 44, 45, 45, 46]

    assert standard_calc(
        Format.gen9vgc(),
        PokemonBuilder("cosmoem").build(),
        PokemonBuilder("electrode").build(),
        "heatcrash",
    ) == [25, 25, 26, 26, 26, 27, 27, 27, 27, 28, 28, 28, 29, 29, 29, 30]
