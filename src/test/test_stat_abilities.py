from pokemon_damage_calculator.calc.calcbuilder import Format, GameState
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.model.enums import Ability, Stat, Terrain, Weather
from test.testutils import flareon


def test_blaze():
    cinderace = (
        PokemonBuilder("Cinderace").ability(Ability.Blaze).ev(Stat.HP, 4).build()
    )
    game_state = GameState(
        Format.gen9vgc(),
        cinderace,
        flareon(),
    )
    # Without blaze
    cinderace.current_hp = 53  # 1/3
    assert game_state.calc("flamethrower") == [
        15,
        15,
        15,
        16,
        16,
        16,
        16,
        17,
        17,
        17,
        17,
        18,
        18,
        18,
        18,
        18,
    ]

    # With blaze
    cinderace.current_hp = 52  # 1/3
    assert game_state.calc("flamethrower") == [
        23,
        23,
        24,
        24,
        24,
        24,
        24,
        25,
        25,
        25,
        26,
        26,
        26,
        27,
        27,
        27,
    ]


# def test_gorilla_tactics():
#     game_state = GameState(
#         Format.gen9vgc(),
#         PokemonBuilder("darmanitangalar").ability(Ability.GorillaTactics),
#         flareon(),
#     )
#     assert game_state.calc("closecombat") == [
#         107,
#         109,
#         110,
#         111,
#         113,
#         114,
#         115,
#         116,
#         118,
#         119,
#         120,
#         121,
#         123,
#         124,
#         125,
#         127,
#     ]


def test_surge_surfer():
    raichu_alola = PokemonBuilder("raichualola").ability(Ability.SurgeSurfer).build()
    game_state = GameState(
        Format.gen9vgc(),
        raichu_alola,
        flareon(),
    )
    game_state.terrain = Terrain.Electric
    assert raichu_alola.stat(Stat.Speed, game_state) == 260


def test_chlorophyll():
    lilligant_hisui = (
        PokemonBuilder("Lilligant-Hisui").ability(Ability.Chlorophyll).build()
    )
    game_state = GameState(
        Format.gen9vgc(),
        lilligant_hisui,
        flareon(),
    )
    game_state.weather = Weather.SunnyDay
    assert lilligant_hisui.stat(Stat.Speed, game_state) == 250


def test_huge_power():
    azumarill = PokemonBuilder("azumarill").ability(Ability.HugePower).build()
    game_state = GameState(
        Format.gen9vgc(),
        azumarill,
        flareon(),
    )
    assert azumarill.stat(Stat.Speed, game_state) == 70  # Not doubled

    assert game_state.calc("aquatail") == [
        140,
        144,
        144,
        146,
        146,
        150,
        150,
        152,
        156,
        156,
        158,
        158,
        162,
        162,
        164,
        168,
    ]
