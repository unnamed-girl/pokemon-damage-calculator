from dataclasses import dataclass
import logging
import math
from pokemon_damage_calculator.calc.base_power_callbacks import (
    electro_ball,
    heavy_slam,
    low_kick,
)
from pokemon_damage_calculator.calc.utils import pokemon_round
from pokemon_damage_calculator.model.enums import (
    Ability,
    MoveCategory,
    MoveFlag,
    PokemonType,
    Stat,
    Status,
    Terrain,
    TypeMatchup,
    UniqueOffensivePokemon,
    Weather,
)

from typing import TYPE_CHECKING

from pokemon_damage_calculator.model.models import Move
from pokemon_damage_calculator.utils import TYPE_CHART

if TYPE_CHECKING:
    from pokemon_damage_calculator.calc.pokemon import Pokemon
    from pokemon_damage_calculator.calc.calcbuilder import GameState
    from pokemon_damage_calculator.calc.damage_calc import _MoveDetails

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

    # Other
    match pokemon.ability:
        case Ability.DauntlessShield:
            apply_boost(pokemon, game_state, Stat.Defence, 1, False)
        case Ability.IntrepidSword:
            apply_boost(pokemon, game_state, Stat.Attack, 1, False)
        # if attacker.has_ability(Ability.DauntlessShield) and move.name == "Body Press":
    #     attack = math.floor(attack * 1.5)
    # if offense_stat == Stat.Attack and attacker.has_ability(Ability.IntrepidSword):
    #     attack = math.floor(attack * 1.5)
    # if defense_stat == Stat.Defence and target.has_ability(Ability.DauntlessShield):
    #     defence = math.floor(attack * 1.5)


def apply_boost(
    pokemon: "Pokemon",
    game_state: "GameState",
    stat: Stat,
    stages: int,
    hostile_source: bool,
):
    if hostile_source and stages < 0:
        # TODO otherss, e.g. mirror armour
        match pokemon.ability:
            case Ability.Defiant:
                apply_boost(pokemon, game_state, Stat.Attack, 2, False)
            case Ability.Competitive:
                apply_boost(pokemon, game_state, Stat.SpecialAttack, 2, False)
    pokemon.boosts[stat] = min(max(pokemon.boosts[stat] + stages, -6), 6)


@dataclass
class _ChainMultiplier:
    numerator: int
    """denominator is 4096"""
    order: int
    """Lowest first"""


def _resolve_chain(value: int, chain: list[_ChainMultiplier]) -> int:
    combined_multiplier = 4096

    chain.sort(key=lambda mul: mul.order)

    for mult in chain:
        combined_multiplier = round(combined_multiplier * mult.numerator / 4096)

    return pokemon_round(value * combined_multiplier / 4096)


def calc_base_power(
    attacker: "Pokemon",
    target: "Pokemon",
    move: Move,
    game_state: "GameState",
) -> int:
    basePower = move.basePower
    if move.basePowerCallback:
        if move.name in ["Heavy Slam", "Heat Crash"]:
            basePower = heavy_slam(attacker.species.weightkg, target.species.weightkg)
        elif move.name == "Low Kick":
            basePower = low_kick(target.species.weightkg)
        elif move.name == "Electro Ball":
            basePower = electro_ball(
                attacker.stat(Stat.Speed, game_state),
                target.stat(Stat.Speed, game_state),
            )
        else:
            logger.error("Didn't handle base power callback for %s", move.name)
    return basePower


def calc_move_type(
    attacker: "Pokemon",
    target: "Pokemon",
    move: Move,
    game_state: "GameState",
) -> PokemonType:
    altered_move_type = move.type
    match attacker.ability:
        case Ability.Aerilate if altered_move_type == PokemonType.Normal:
            altered_move_type = PokemonType.Flying
        case Ability.Galvanize if altered_move_type == PokemonType.Normal:
            altered_move_type = PokemonType.Electric
        case Ability.Pixilate if altered_move_type == PokemonType.Normal:
            altered_move_type = PokemonType.Fairy
        case Ability.Refrigerate if altered_move_type == PokemonType.Normal:
            altered_move_type = PokemonType.Ice
        case Ability.LiquidVoice if move.has_flag(MoveFlag.Sound):
            altered_move_type = PokemonType.Water
        case Ability.Normalize if move.has_flag(MoveFlag.Sound):
            name = move.realMove or move.name
            if not move.isZ:
                if name not in [
                    "hiddenpower",
                    "weatherball",
                    "naturalgift",
                    "technoblast",
                    "judgment",
                    "multiattack",
                    "terrainpulse",
                ]:
                    altered_move_type = PokemonType.Normal
    return altered_move_type


class _EffectivePowerMults:
    AURA_BREAK = _ChainMultiplier(3072, 1)
    RIVALRY = _ChainMultiplier(3072, 2)
    ONE_TWO_ABILITY = _ChainMultiplier(4915, 3)
    BATTERY = _ChainMultiplier(5325, 4)
    ONE_THREE_ABILITY = _ChainMultiplier(5325, 5)
    AURA = _ChainMultiplier(5448, 6)
    ONE_FIVE_ABILITY = _ChainMultiplier(6144, 7)
    HEATPROOF = _ChainMultiplier(2048, 8)
    DRY_SKIN = _ChainMultiplier(5120, 9)
    ONE_ONE_ITEM = _ChainMultiplier(4505, 10)
    ONE_TWO_ITEM = _ChainMultiplier(4915, 11)
    NORMAL_GEM = _ChainMultiplier(5325, 12)
    SOLAR_BAD_WEATHER = _ChainMultiplier(2048, 13)
    ME_FIRST = _ChainMultiplier(6144, 14)
    KNOCK_OFF = _ChainMultiplier(6144, 15)
    HELPING_HAND = _ChainMultiplier(6144, 16)
    CHARGE = _ChainMultiplier(8192, 17)
    DOUBLE_MOVE = _ChainMultiplier(8192, 18)
    TERRAIN_DEFENCE = _ChainMultiplier(2048, 19)
    TERRAIN_OFFENCE = _ChainMultiplier(6144, 20)
    SPORT = _ChainMultiplier(1352, 21)


def calc_effective_power(
    attacker: "Pokemon",
    target: "Pokemon",
    move: "_MoveDetails",
    game_state: "GameState",
    base_power: int,
) -> int:
    chain: list[_ChainMultiplier] = []

    # Auras
    fairy_aura = any(
        pokemon.ability == Ability.FairyAura for pokemon in game_state.pokemon
    )
    dark_aura = any(
        pokemon.ability == Ability.DarkAura for pokemon in game_state.pokemon
    )
    aura_break = any(
        pokemon.ability == Ability.AuraBreak for pokemon in game_state.pokemon
    )
    if aura_break and (
        (fairy_aura and move.type == PokemonType.Fairy)
        or (dark_aura and move.type == PokemonType.Dark)
    ):
        chain.append(_EffectivePowerMults.AURA_BREAK)
    elif dark_aura and move.type == PokemonType.Dark:
        chain.append(_EffectivePowerMults.AURA)
    elif fairy_aura and move.type == PokemonType.Fairy:
        chain.append(_EffectivePowerMults.AURA)

    # Attacker abiltiies
    match attacker.ability:
        case Ability.Aerilate if move.base_move.type == PokemonType.Normal:
            chain.append(_EffectivePowerMults.ONE_TWO_ABILITY)
        # TODO analytic
        # TODO Battery
        case Ability.FlareBoost if (
            attacker.status == Status.Burn
            and move.base_move.category == MoveCategory.Special
        ):
            chain.append(_EffectivePowerMults.ONE_FIVE_ABILITY)
        case Ability.IronFist if move.base_move.has_flag(MoveFlag.Punch):
            chain.append(_EffectivePowerMults.ONE_TWO_ABILITY)
        case Ability.Galvanize if move.base_move.type == PokemonType.Normal:
            chain.append(_EffectivePowerMults.ONE_TWO_ABILITY)
        case Ability.MegaLauncher if move.base_move.has_flag(MoveFlag.Pulse):
            chain.append(_EffectivePowerMults.ONE_FIVE_ABILITY)
        case Ability.Normalize:
            chain.append(_EffectivePowerMults.ONE_TWO_ABILITY)
        case Ability.Pixilate if move.base_move.type == PokemonType.Normal:
            chain.append(_EffectivePowerMults.ONE_TWO_ABILITY)
        case Ability.Reckless if move.base_move.recoil or move.base_move.hasCrashDamage:
            chain.append(_EffectivePowerMults.ONE_TWO_ABILITY)
        case Ability.PunkRock if move.base_move.has_flag(MoveFlag.Sound):
            chain.append(_EffectivePowerMults.ONE_THREE_ABILITY)
        case Ability.Refrigerate if move.base_move.type == PokemonType.Normal:
            chain.append(_EffectivePowerMults.ONE_TWO_ABILITY)
        # TODO Rivalry
        case Ability.SandForce if (
            game_state.weather == Weather.Sandstorm
            and move.type in [PokemonType.Rock, PokemonType.Ground, PokemonType.Steel]
        ):
            chain.append(_EffectivePowerMults.ONE_THREE_ABILITY)
        case Ability.Sharpness if move.base_move.has_flag(MoveFlag.Slicing):
            chain.append(_EffectivePowerMults.ONE_FIVE_ABILITY)
        case Ability.SheerForce if move.base_move.hasSheerForce:
            chain.append(_EffectivePowerMults.ONE_THREE_ABILITY)
        case Ability.StrongJaw if move.base_move.has_flag(MoveFlag.Bite):
            chain.append(_EffectivePowerMults.ONE_FIVE_ABILITY)
        case Ability.ToughClaws if move.contact:
            chain.append(_EffectivePowerMults.ONE_THREE_ABILITY)
        case Ability.ToxicBoost if (
            attacker.status == Status.Poison or attacker.status == Status.Toxic
        ) and move.base_move.category == MoveCategory.Physical:
            chain.append(_EffectivePowerMults.ONE_FIVE_ABILITY)

    # Defender abilities
    if not move.ignores_ability:
        match target.ability:
            case Ability.DrySkin if move.type == PokemonType.Fire:
                chain.append(_EffectivePowerMults.DRY_SKIN)
            case Ability.Heatproof if move.type == PokemonType.Fire:
                chain.append(_EffectivePowerMults.HEATPROOF)

    # Items
    # TODO

    # Moves
    match move.base_move.name:
        case "Brine" if target.current_hp <= math.floor(
            target.stat(Stat.HP, game_state) / 2
        ):
            chain.append(_EffectivePowerMults.DOUBLE_MOVE)
        case "Facade" if attacker.status is not None:
            chain.append(_EffectivePowerMults.DOUBLE_MOVE)
        # TODO Fusion Bolt
        # TODO Fusion FLare
        # TODO Knock Off
        # TODO Retaliate
        case "Solar Beam" if game_state.weather not in [
            Weather.NONE,
            Weather.SunnyDay,
            Weather.ExtremelyHarshSunlight,
            Weather.StrongWinds,
        ]:
            chain.append(_EffectivePowerMults.SOLAR_BAD_WEATHER)
        case "Solar Blade" if game_state.weather not in [
            Weather.NONE,
            Weather.SunnyDay,
            Weather.ExtremelyHarshSunlight,
            Weather.StrongWinds,
        ]:
            chain.append(_EffectivePowerMults.SOLAR_BAD_WEATHER)
        case "Venoshock" if target.status in [Status.Poison, Status.Toxic]:
            chain.append(_EffectivePowerMults.DOUBLE_MOVE)

    # Terrains
    if target.is_grounded(move.ignores_ability):
        match game_state.terrain:
            case Terrain.Grassy if move.base_move.name in [
                "Earthquake",
                "Bulldoze",
                "Magnitude",
            ]:
                chain.append(_EffectivePowerMults.TERRAIN_DEFENCE)
            case Terrain.Misty if move.type == PokemonType.Dragon:
                chain.append(_EffectivePowerMults.TERRAIN_DEFENCE)

    if attacker.is_grounded(False):
        match game_state.terrain:
            case Terrain.Electric if move.type == PokemonType.Electric:
                chain.append(_EffectivePowerMults.TERRAIN_OFFENCE)
            case Terrain.Grassy if move.type == PokemonType.Grass:
                chain.append(_EffectivePowerMults.TERRAIN_OFFENCE)
            case Terrain.Psychic if move.type == PokemonType.Psychic:
                chain.append(_EffectivePowerMults.TERRAIN_OFFENCE)
    # TODO Sport

    # Other
    # TODO Charge
    # TODO Helping Hand
    # TODO Me First

    bp_before_technician = _resolve_chain(
        base_power,
        [
            mult
            for mult in chain
            if mult.order < _EffectivePowerMults.ONE_FIVE_ABILITY.order
        ],
    )
    if attacker.ability == Ability.Technician and bp_before_technician <= 60:
        chain.append(_EffectivePowerMults.ONE_FIVE_ABILITY)

    logger.info("Effective power chain: %s", chain)
    return _resolve_chain(base_power, chain)


class _EffectiveAttackMults:
    HALF_OFFENCE = _ChainMultiplier(2048, 1)
    FLOWER_GIFT = _ChainMultiplier(6144, 2)
    FIFTY_OFFENCE = _ChainMultiplier(6144, 3)
    DOUBLE_OFFENCE = _ChainMultiplier(8192, 4)
    HALF_DEFENCE = _ChainMultiplier(2048, 5)
    CHOICE_ITEMS = _ChainMultiplier(6144, 6)
    UNIQUE_ITEM_DOUBLERS = _ChainMultiplier(8192, 7)


def calc_effective_attack(
    attacker: "Pokemon",
    target: "Pokemon",
    move: "_MoveDetails",
    game_state: "GameState",
) -> int:
    match move.base_move.category:
        case MoveCategory.Physical:
            offense_stat = Stat.Attack
        case MoveCategory.Special:
            offense_stat = Stat.SpecialAttack
        case MoveCategory.Status:
            raise ValueError("This move doesn't have an effective attack")

    match move.base_move.overrideOffensivePokemon:
        case None:
            stat_source = attacker
        case UniqueOffensivePokemon.FoulPlay:
            stat_source = target

    attack: int = stat_source.stat(
        move.base_move.overrideOffensiveStat or offense_stat, game_state
    )

    if not target.ability == Ability.Unaware:
        if move.crits:  # || boost > 0
            # TODO boosts,
            pass

    if attacker.ability == Ability.Hustle:
        attack = pokemon_round(attack * 6144 / 4096)
    if (
        attacker.ability == Ability.HadronEngine
        and move.base_move.category == MoveCategory.Special
        and game_state.terrain == Terrain.Electric
    ):
        attack = pokemon_round(attack * 5461 / 4096)
    if (
        attacker.ability == Ability.OrichalcumPulse
        and move.base_move.category == MoveCategory.Physical
        and game_state.weather
        in [
            Weather.SunnyDay,
            Weather.ExtremelyHarshSunlight,
        ]
    ):
        attack = pokemon_round(attack * 5461 / 4096)
    chain: list[_ChainMultiplier] = []

    # Attacker Abilities
    match attacker.ability:
        case Ability.Blaze if (
            move.type == PokemonType.Fire
            and attacker.current_hp
            <= math.floor(attacker.stat(Stat.HP, game_state) / 3)
        ):
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.Defeatist if attacker.current_hp <= math.floor(
            attacker.stat(Stat.HP, game_state) / 2
        ):
            chain.append(_EffectiveAttackMults.HALF_OFFENCE)
        # TODO Flash Fire
        # TODO Flower Gift
        case Ability.GorillaTactics if move.base_move.category == MoveCategory.Physical:
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.Guts if attacker.status is not None:
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.HugePower if move.base_move.category == MoveCategory.Physical:
            chain.append(_EffectiveAttackMults.DOUBLE_OFFENCE)
        # TODO Minus
        case Ability.Overgrow if (
            move.type == PokemonType.Grass
            and attacker.current_hp
            <= math.floor(attacker.stat(Stat.HP, game_state) / 3)
        ):
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        # TODO Plus
        case Ability.PurePower if move.base_move.category == MoveCategory.Physical:
            chain.append(_EffectiveAttackMults.DOUBLE_OFFENCE)
        case Ability.SlowStart if (
            move.base_move.category == MoveCategory.Physical
        ):  # TODO Z-moves are weird
            chain.append(_EffectiveAttackMults.HALF_OFFENCE)
        case Ability.SolarPower if (
            move.base_move.category == MoveCategory.Special
            and game_state.weather
            in [
                Weather.SunnyDay,
                Weather.ExtremelyHarshSunlight,
            ]
        ):
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.Swarm if (
            move.type == PokemonType.Bug
            and attacker.current_hp
            <= math.floor(attacker.stat(Stat.HP, game_state) / 3)
        ):
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.Torrent if (
            move.type == PokemonType.Water
            and attacker.current_hp
            <= math.floor(attacker.stat(Stat.HP, game_state) / 3)
        ):
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.DragonsMaw if move.type == PokemonType.Dragon:
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.RockyPayload if move.type == PokemonType.Rock:
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.SteelySpirit if move.type == PokemonType.Steel:
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
            # TODO Ally
        case Ability.Steelworker if move.type == PokemonType.Steel:
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.Transistor if move.type == PokemonType.Electric:
            chain.append(_EffectiveAttackMults.FIFTY_OFFENCE)
        case Ability.WaterBubble if move.type == PokemonType.Water:
            chain.append(_EffectiveAttackMults.DOUBLE_OFFENCE)

    # Defender abilities
    if not move.ignores_ability:
        match target.ability:
            case Ability.PurifyingSalt if move.type == PokemonType.Ghost:
                chain.append(_EffectiveAttackMults.HALF_DEFENCE)
            case Ability.PurifyingSalt if move.type in [
                PokemonType.Fire,
                PokemonType.Ice,
            ]:
                chain.append(_EffectiveAttackMults.HALF_DEFENCE)

    # TODO items

    logger.info("Attack %s, Effective attack chain: %s", attack, chain)
    return _resolve_chain(attack, chain)


class _EffectiveDefenceMults:
    FLOWER_GIFT = _ChainMultiplier(6144, 1)
    ONE_FIVE_ABILITIES = _ChainMultiplier(6144, 2)
    FUR_COAT = _ChainMultiplier(8192, 3)
    ONE_FIVE_ITEM = _ChainMultiplier(6144, 4)
    DOUBLE_ITEM = _ChainMultiplier(8192, 4)


def calc_effective_defence(
    attacker: "Pokemon",
    target: "Pokemon",
    move: "_MoveDetails",
    game_state: "GameState",
) -> int:
    match move.base_move.category:
        case MoveCategory.Physical:
            defense_stat = Stat.Defence
        case MoveCategory.Special:
            defense_stat = Stat.SpecialDefence
        case MoveCategory.Status:
            raise ValueError("This move doesn't have an effective attack")
    defence_stat = move.base_move.overrideDefensiveStat or defense_stat
    defence: int = target.stat(defence_stat, game_state)

    match game_state.weather:
        case Weather.Sandstorm if PokemonType.Rock in target.get_types():
            defence = pokemon_round(defence * 6144 / 4096)
        case Weather.Snow if PokemonType.Ice in target.get_types():
            defence = pokemon_round(defence * 6144 / 4096)

    # TODO boosts (unaware, chip away, sacred sword)

    chain: list[_ChainMultiplier] = []

    # Defence abilities
    match target.ability:
        # TODO Flower Gift
        case Ability.FurCoat if defence_stat == Stat.Defence:
            chain.append(_EffectiveDefenceMults.FUR_COAT)
        case Ability.GrassPelt if (
            game_state.terrain == Terrain.Grassy and defence_stat == Stat.Defence
        ):
            chain.append(_EffectiveDefenceMults.ONE_FIVE_ABILITIES)
        case Ability.MarvelScale if attacker.status is not None:
            chain.append(_EffectiveDefenceMults.ONE_FIVE_ABILITIES)
    # TODO items

    return defence


def calc_type_effectiveness(
    attacker: "Pokemon",
    target: "Pokemon",
    move: "_MoveDetails",
    game_state: "GameState",
) -> float:
    # TODO Iron Ball
    # TODO Ring Target
    if (
        move.base_move.name == "Thousand Arrows"
        and PokemonType.Flying in target.get_types()
    ):
        return TypeMatchup.Neutral

    type_effectiveness = TypeMatchup.Neutral
    for poke_type in target.species.types:
        multiplier = TYPE_CHART[poke_type].get(move.type, TypeMatchup.Neutral)
        if (
            poke_type == PokemonType.Flying
            and game_state.weather == Weather.StrongWinds
            and multiplier == TypeMatchup.SuperEffective
        ):
            continue
        if (
            move.type in [PokemonType.Fighting, PokemonType.Normal]
            and poke_type == PokemonType.Ghost
        ):
            continue
        if move.base_move.name == "Freeze-Dry" and poke_type == PokemonType.Water:
            type_effectiveness *= TypeMatchup.SuperEffective
            continue
        type_effectiveness *= multiplier

    if move.base_move.name == "Flying Press":
        type_effectiveness *= TYPE_CHART[PokemonType.Flying].get(
            move.type, TypeMatchup.Neutral
        )

    return type_effectiveness


def calc_other_multipliers(
    attacker: "Pokemon",
    target: "Pokemon",
    move: "_MoveDetails",
    game_state: "GameState",
) -> float:
    """
    https://web.archive.org/web/20240516021936/https://www.trainertower.com/dawoblefets-damage-dissertation/#final-mods
    """
    # TODO screens

    # Defneder abilities
    if not move.ignores_ability:
        pass  # TODO all of this

        # if move.type == PokemonType.Fire and target.has_ability(Ability.DrySkin):
        #     other_multipliers *= 1.25
        # if altered_move_type == PokemonType.Fire and target.has_ability(Ability.Fluffy):
        #     other_multipliers *= 2
        # if make_contact and target.has_ability(Ability.Fluffy):
        #     other_multipliers *= 0.5
        # # TODO Multiscale
        # # TODO Shadow Shield (NOT IGNORABLE)
        # if move.has_flag(MoveFlag.Sound) and target.has_ability(Ability.PunkRock):
        #     other_multipliers *= 0.5

        # if move.category == MoveCategory.Special and target.has_ability(
        #     Ability.IceScales
        # ):
        #     other_multipliers *= 0.5
    return 1.0


def calc_immunities(
    attacker: "Pokemon",
    target: "Pokemon",
    move: "_MoveDetails",
    game_state: "GameState",
    type_effectiveness: float,
) -> bool:
    if not move.ignores_ability:
        flag_immunities = [
            (Ability.WindRider, MoveFlag.Wind),
            (Ability.Bulletproof, MoveFlag.Bullet),
            (Ability.Soundproof, MoveFlag.Sound),
        ]
        for ability, flag in flag_immunities:
            if move.base_move.has_flag(flag) and target.has_ability(ability):
                return True
        type_immunities = [
            (Ability.EarthEater, PokemonType.Ground),
            (Ability.FlashFire, PokemonType.Fire),
            (Ability.DrySkin, PokemonType.Water),
            (Ability.Levitate, PokemonType.Ground),
            (Ability.LightningRod, PokemonType.Electric),
            (Ability.MotorDrive, PokemonType.Electric),
            (Ability.SapSipper, PokemonType.Grass),
            (Ability.StormDrain, PokemonType.Water),
            (Ability.VoltAbsorb, PokemonType.Electric),
            (Ability.WaterAbsorb, PokemonType.Water),
            (Ability.WellBakedBody, PokemonType.Fire),
        ]
        for ability, type_ in type_immunities:
            if move.type == type_ and target.has_ability(ability):
                return True

        # TODO Disguise

        if target.has_ability(Ability.WonderGuard) and not type_effectiveness > 1.0:
            return True
    return False


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
