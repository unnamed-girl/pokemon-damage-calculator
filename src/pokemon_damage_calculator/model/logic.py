from pokemon_damage_calculator.calc.pokemon import Pokemon
from pokemon_damage_calculator.model.enums import Ability, Terrain, Weather

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pokemon_damage_calculator.calc.calcbuilder import Field


def enters_effects(pokemon: Pokemon, field: "Field"):
    # Terrain
    match pokemon.ability:
        case Ability.GrassySurge:
            field.terrain = Terrain.Grassy
        case Ability.ElectricSurge:
            field.terrain = Terrain.Electric
        case Ability.PsychicSurge:
            field.terrain = Terrain.Psychic
        case Ability.MistySurge:
            field.terrain = Terrain.Misty

    # Weather
    match pokemon.ability:
        case Ability.DesolateLand:
            field.weather = Weather.ExtremelyHarshSunlight
        case Ability.PrimordialSea:
            field.weather = Weather.HeavyRain
        case Ability.DeltaStream:
            field.weather = Weather.StrongWinds
        case Ability.Drought if not field.weather.difficult_to_override():
            field.weather = Weather.SunnyDay
        case Ability.OrichalcumPulse if not field.weather.difficult_to_override():
            field.weather = Weather.SunnyDay
        case Ability.Drizzle if not field.weather.difficult_to_override():
            field.weather = Weather.RainDance
