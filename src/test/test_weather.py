from pokemon_damage_calculator.calc.calcbuilder import Format
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.model.enums import Ability, Weather
from test.testutils import standard_calc


def test_weather_order():
    # Pelipper is FASTER, so its sunny
    assert (
        Format.gen9vgc()
        .game(
            PokemonBuilder("electrode").ability(Ability.Drizzle),
            PokemonBuilder("cosmoem").ability(Ability.Drought),
        )
        .weather
        == Weather.SunnyDay
    )


def test_weather_order_2():
    assert (
        Format.gen9vgc()
        .game(
            PokemonBuilder("electrode").ability(Ability.Drought),
            PokemonBuilder("cosmoem").ability(Ability.Drizzle),
        )
        .weather
        == Weather.RainDance
    )


def test_weak_after_strong_weather():
    assert (
        Format.gen9vgc()
        .game(
            PokemonBuilder("electrode").ability(Ability.DesolateLand),
            PokemonBuilder("cosmoem").ability(Ability.Drizzle),
        )
        .weather
        == Weather.ExtremelyHarshSunlight
    )


def test_strong_after_strong_weather():
    assert (
        Format.gen9vgc()
        .game(
            PokemonBuilder("electrode").ability(Ability.DesolateLand),
            PokemonBuilder("cosmoem").ability(Ability.PrimordialSea),
        )
        .weather
        == Weather.HeavyRain
    )


def test_weather_effect():
    assert standard_calc(
        Format.gen9vgc(),
        (PokemonBuilder("ninetales").ability(Ability.Drought)),
        (PokemonBuilder("pelipper")),
        "flamethrower",
    ) == [43, 44, 45, 45, 45, 46, 46, 47, 48, 48, 48, 49, 49, 50, 51, 51]

def test_snow():
    game = Format.gen9vgc().game(
        PokemonBuilder("regice"),
        PokemonBuilder("regice")
        )
    game.weather = Weather.Snow
    assert game.calc("closecombat") == [36, 36, 38, 38, 38, 38, 40, 40, 40, 40, 40, 42, 42, 42, 42, 44]