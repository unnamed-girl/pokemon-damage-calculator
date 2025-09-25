from pokemon_damage_calculator.calc.calcbuilder import CalcBuilder
from pokemon_damage_calculator.model.enums import Stat
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.model.natures import Nature


def flareon():
    return (
        PokemonBuilder("flareon")
        .ev(Stat.Defence, 99)
        .ev(Stat.SpecialDefence, 99)
        .nature(Nature.BOLD)
        .build()
    )


def test_damage_calc_evs():
    damage = CalcBuilder.gen9vgc().calc(
        (
            PokemonBuilder("rillaboom")
            .ev(Stat.Attack, 184)
            .nature(Nature.ADAMANT)
            .build()
        ),
        flareon(),
        "stompingtantrum",
    )

    assert damage == [
        104,
        106,
        106,
        108,
        110,
        110,
        112,
        114,
        114,
        116,
        116,
        118,
        120,
        120,
        122,
        124,
    ]


def test_damage_calc_resist():
    swampert = PokemonBuilder("swampert").build()
    damage = CalcBuilder.gen9vgc().calc(
        swampert,
        swampert,
        "hydropump",
    )

    assert damage == [60, 61, 61, 63, 63, 64, 64, 66, 66, 67, 67, 69, 69, 70, 70, 72]


def test_auto_crit():
    assert CalcBuilder.gen9vgc().calc(
        (PokemonBuilder("urshifurapidstrike").build()),
        flareon(),
        "surgingstrikes",
    ) == [
        198,
        204,
        204,
        204,
        216,
        216,
        216,
        216,
        222,
        222,
        222,
        222,
        234,
        234,
        234,
        240,
    ]

    assert CalcBuilder.gen9vgc().calc(
        (PokemonBuilder("swampert").ev(Stat.Attack, 252).build()),
        flareon(),
        "wickedblow",
    ) == [68, 69, 70, 71, 72, 72, 73, 74, 75, 76, 76, 77, 78, 79, 80, 81]
