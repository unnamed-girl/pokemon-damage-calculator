import logging
import math
from pokemon_damage_calculator.model.enums import (
    Ability,
    MoveCategory,
    PokemonType,
    Stat,
    Status,
    Terrain,
    Weather,
)

from typing import TYPE_CHECKING

from pokemon_damage_calculator.model.models import Move

if TYPE_CHECKING:
    from pokemon_damage_calculator.calc.pokemon import Pokemon
    from pokemon_damage_calculator.calc.calcbuilder import GameState

logger = logging.getLogger()


def enters_effects(pokemon: "Pokemon", game_state: "GameState"):
    # Terrain
    match pokemon.ability:
        case Ability.GrassySurge:
            game_state.terrain = Terrain.Grassy
        case Ability.ElectricSurge:
            game_state.terrain = Terrain.Electric
        case Ability.PsychicSurge:
            game_state.terrain = Terrain.Psychic
        case Ability.MistySurge:
            game_state.terrain = Terrain.Misty

    # Weather
    match pokemon.ability:
        case Ability.DesolateLand:
            game_state.weather = Weather.ExtremelyHarshSunlight
        case Ability.PrimordialSea:
            game_state.weather = Weather.HeavyRain
        case Ability.DeltaStream:
            game_state.weather = Weather.StrongWinds
        case Ability.Drought if not game_state.weather.difficult_to_override():
            game_state.weather = Weather.SunnyDay
        case Ability.OrichalcumPulse if not game_state.weather.difficult_to_override():
            game_state.weather = Weather.SunnyDay
        case Ability.Drizzle if not game_state.weather.difficult_to_override():
            game_state.weather = Weather.RainDance


def damage_calc_attack_stat_modification(
    pokemon: "Pokemon", game_state: "GameState", move: Move, result: int
) -> int:
    multiplier = 1
    match pokemon.ability:
        case Ability.Blaze if (
            move.type == PokemonType.Fire
            and pokemon.current_hp / pokemon.stat(Stat.HP, game_state) <= 1 / 3
        ):
            multiplier *= 1.5
        # TODO Flash Fire
        case Ability.GorillaTactics if move.category == MoveCategory.Physical:
            multiplier *= 1.5
        case Ability.Guts if pokemon.status is not None:
            multiplier *= 1.5
        case Ability.HadronEngine if (
            move.category == MoveCategory.Special
            and game_state.terrain == Terrain.Electric
        ):
            multiplier *= 5461 / 4096
        case Ability.HugePower if move.category == MoveCategory.Physical:
            multiplier *= 2.0
        case Ability.Hustle if move.category == MoveCategory.Physical:
            multiplier *= 3277 / 4096
            # TODO accuracy
        case Ability.OrichalcumPulse if (
            move.category == MoveCategory.Physical
            and game_state.weather
            in [
                Weather.SunnyDay,
                Weather.ExtremelyHarshSunlight,
            ]
        ):
            multiplier *= 5461 / 4096
        case Ability.Overgrow if (
            move.type == PokemonType.Grass
            and pokemon.current_hp / pokemon.stat(Stat.HP, game_state) <= 1 / 3
        ):
            multiplier *= 1.5
        case Ability.PurePower if move.category == MoveCategory.Physical:
            multiplier *= 2.0
        case Ability.SolarPower if (
            move.category == MoveCategory.Special
            and game_state.weather
            in [
                Weather.SunnyDay,
                Weather.ExtremelyHarshSunlight,
            ]
        ):
            multiplier *= 1.5
        case Ability.Swarm if (
            move.type == PokemonType.Bug
            and pokemon.current_hp / pokemon.stat(Stat.HP, game_state) <= 1 / 3
        ):
            multiplier *= 1.5
        case Ability.Torrent if (
            move.type == PokemonType.Water
            and pokemon.current_hp / pokemon.stat(Stat.HP, game_state) <= 1 / 3
        ):
            multiplier *= 1.5
    if pokemon.status == Status.Burn and not pokemon.ability == Ability.Guts:
        multiplier *= 0.5
    if multiplier != 1:
        logger.info(
            "%s's %s Multiplier: %s", pokemon.species.name, move.name, multiplier
        )
    return math.floor(result * multiplier)


# damage_calc_defense_stat_modification
# TODO marvel scale


def stat_modifications(
    pokemon: "Pokemon", game_state: "GameState", stat: Stat, result: int
) -> int:
    multiplier = 1
    match pokemon.ability:
        case Ability.Chlorophyll if (
            stat == Stat.Speed and game_state.weather == Weather.SunnyDay
        ):
            multiplier *= 2
        # TODO Flower Gift
        case Ability.GrassPelt if (
            stat == Stat.Defence and game_state.terrain == Terrain.Grassy
        ):
            # TODO handle confusion
            multiplier *= 1.5
        # TODO minus
        # TODO plus
        case Ability.SurgeSurfer if (
            stat == Stat.Speed and game_state.terrain == Terrain.Electric
        ):
            multiplier *= 2
        # TODO protosynthesis
        # TODO quark drive
        case Ability.QuickFeet if pokemon.status is not None:
            multiplier *= 1.5
        case Ability.SandRush if game_state.weather == Weather.Sandstorm:
            multiplier *= 2.0
        case Ability.SlushRush if game_state.weather in [Weather.Hail, Weather.Snow]:
            multiplier *= 2.0
        case Ability.SwiftSwim if game_state.weather in [
            Weather.RainDance,
            Weather.HeavyRain,
        ]:
            multiplier *= 2.0
        case Ability.Unburden if pokemon.item is None:
            multiplier *= 2.0
    if pokemon.status == Status.Paralysis and stat == Stat.Speed:
        multiplier *= 0.5
    if multiplier != 1:
        logger.info("%s's %s Multiplier: %s", pokemon.species.name, stat, multiplier)
    return math.floor(result * multiplier)
