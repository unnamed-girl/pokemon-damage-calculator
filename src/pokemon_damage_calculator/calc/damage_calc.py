import logging
import math

from pokemon_damage_calculator.calc.base_power_callbacks import (
    electro_ball,
    heavy_slam,
    low_kick,
)
from pokemon_damage_calculator.model.enums import (
    Ability,
    MoveCategory,
    MoveFlag,
    PokemonType,
    Stat,
    Target,
    TypeMatchup,
    UniqueOffensivePokemon,
)
from pokemon_damage_calculator.model.models import Move

from .pokemon import Pokemon
from ..utils import TYPE_CHART

logger = logging.getLogger()


def floored_multiply(damage_range: list[int], multiplier: float) -> list[int]:
    return [math.floor(d * multiplier) for d in damage_range]


EPSILON = 0.0001


def pokemon_round(n: float) -> int:
    return round(n - EPSILON)


def pokerounded_multiply(damage_range: list[int], multiplier: float) -> list[int]:
    return [pokemon_round(d * multiplier) for d in damage_range]


def damage_calc(move: Move, attacker: "Pokemon", target: "Pokemon") -> list[int]:
    if move.category == MoveCategory.Status:
        return [0]

    match move.category:
        case MoveCategory.Physical:
            offense_stat, defense_stat = Stat.Attack, Stat.Defence
        case MoveCategory.Special:
            offense_stat, defense_stat = Stat.SpecialAttack, Stat.SpecialDefence

    # Overall Properties
    attacker_ignores_abilities = (
        move.ignoreAbility
        or attacker.has_ability(Ability.MoldBreaker)
        or attacker.has_ability(Ability.Turboblaze)
        or attacker.has_ability(Ability.Teravolt)
    )
    make_contact = move.has_flag(MoveFlag.Contact) and not attacker.has_ability(
        Ability.LongReach
    )

    # Overrides
    match move.overrideOffensivePokemon:
        case None:
            attacker_stat_source = attacker
        case UniqueOffensivePokemon.FoulPlay:
            attacker_stat_source = target

    if move.overrideOffensiveStat:
        offense_stat = move.overrideOffensiveStat
    if move.overrideDefensiveStat:
        defense_stat = move.overrideDefensiveStat

    # Initial values
    target_multiplier = (
        1
        if move.target
        in [
            Target.Self,
            Target.AdjacentAlly,
            Target.AdjacentAllyOrSelf,
            Target.AdjacentFoe,
            Target.Any,
            Target.Normal,
            Target.RandomNormal,
            Target.AllyTeam,
            Target.Scripted,
        ]
        else 0.75
    )
    attack = attacker_stat_source.stat(offense_stat)
    defence = target.stat(defense_stat)
    level = attacker.level
    power = move.basePower

    other_modifications = 1

    ###  Attacker Abilities
    ## Type Modification
    altered_move_type = move.type
    if altered_move_type == PokemonType.Normal:
        if attacker.has_ability(Ability.Aerilate):
            other_modifications *= 1.2
            altered_move_type = PokemonType.Flying
        if attacker.has_ability(Ability.Galvanize):
            other_modifications *= 1.2
            altered_move_type = PokemonType.Electric
        if attacker.has_ability(Ability.Pixilate):
            other_modifications *= 1.2
            altered_move_type = PokemonType.Fairy
        if attacker.has_ability(Ability.Refrigerate):
            other_modifications *= 1.2
            altered_move_type = PokemonType.Ice
    if move.has_flag(MoveFlag.Sound):
        if attacker.has_ability(Ability.LiquidVoice):
            altered_move_type = PokemonType.Water
    if attacker.has_ability(Ability.Normalize):
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
                other_modifications *= 1.2
                altered_move_type = PokemonType.Normal
    ## Stat Modification
    # TODO Blaze
    # TODO Overgrow
    # TODO Swarm
    # TODO Torrent
    if altered_move_type == PokemonType.Dragon and attacker.has_ability(
        Ability.DragonsMaw
    ):
        attack *= 1.5
    if altered_move_type == PokemonType.Rock and attacker.has_ability(
        Ability.RockyPayload
    ):
        attack *= 1.5
    if altered_move_type == PokemonType.Steel and attacker.has_ability(
        Ability.Steelworker
    ):
        attack *= 1.5
    if altered_move_type == PokemonType.Electric and attacker.has_ability(
        Ability.Transistor
    ):
        attack *= 1.5

    ## Power Modifications
    if power <= 60 and attacker.has_ability(Ability.Technician):
        power *= 1.5
    if altered_move_type == PokemonType.Water and attacker.has_ability(
        Ability.WaterBubble
    ):
        power *= 2
    ## Misc Power Modification
    # TODO Analytic
    if move.has_flag(MoveFlag.Punch) and attacker.has_ability(Ability.IronFist):
        other_modifications *= 1.2
    if move.has_flag(MoveFlag.Pulse) and attacker.has_ability(Ability.MegaLauncher):
        other_modifications *= 1.5
    if move.has_flag(MoveFlag.Sound) and attacker.has_ability(Ability.PunkRock):
        other_modifications *= 1.3
    if (move.recoil or move.hasCrashDamage) and attacker.has_ability(Ability.Reckless):
        other_modifications *= 1.2
    # TODO Rivalry
    # TODO Sand Force
    if move.has_flag(MoveFlag.Slicing) and attacker.has_ability(Ability.Sharpness):
        other_modifications *= 1.5
    if move.hasSheerForce and attacker.has_ability(Ability.SheerForce):
        other_modifications *= 5325 / 4096
    # TODO Stakeout
    if altered_move_type == PokemonType.Steel and attacker.has_ability(
        Ability.SteelySpirit
    ):
        other_modifications *= 1.5
    if move.has_flag(MoveFlag.Bite) and attacker.has_ability(Ability.StrongJaw):
        other_modifications *= 1.5
    # TODO Supreme Overlord
    if make_contact and attacker.has_ability(Ability.ToughClaws):
        other_modifications *= 5325 / 4096
    # TODO Toxic Boost

    ### Ally Abilities
    # TODO Battery
    # TODO Power Spot
    # TODO Steely Spirit
    # TODO Flower Gift
    # TODO Minus

    ## Get Stat Ability
    # TODO Chlorophyll
    # TODO Flower Gift
    # TODO Fur Coat
    # TODO Gorilla Tactics
    # TODO Grass Pelt
    # TODO Guts
    # TODO Hadron Engine
    # TODO Huge Power
    # TODO Hustle
    # TODO Marvel Scale
    # TODO Orichalcum Pulse
    # TODO Plus
    # TODO Protosynthesis
    # TODO Pure Power
    # TODO Quark Drive
    # TODO Quick Feet
    # TODO Sand Rush
    # TODO Slush Rush
    # TODO Solar Power
    # TODO Surge Surfer
    # TODO Swift Swim
    # TODO Unburden

    ### N/A Abilities
    # Battle Bond

    ### Defender Abilities
    if not attacker_ignores_abilities:
        flag_immunities = [
            (Ability.WindRider, MoveFlag.Wind),
            (Ability.Bulletproof, MoveFlag.Bullet),
            (Ability.Soundproof, MoveFlag.Sound),
        ]
        for ability, flag in flag_immunities:
            if move.has_flag(flag) and target.has_ability(ability):
                return [0]
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
            if altered_move_type == type_ and target.has_ability(ability):
                return [0]

        # TODO Disguise
        if altered_move_type == PokemonType.Fire and target.has_ability(
            Ability.DrySkin
        ):
            other_modifications *= 1.25
        if altered_move_type == PokemonType.Fire and target.has_ability(Ability.Fluffy):
            other_modifications *= 2
        if make_contact and target.has_ability(Ability.Fluffy):
            other_modifications *= 0.5
        if altered_move_type == PokemonType.Fire and target.has_ability(
            Ability.Heatproof
        ):
            attack *= 0.5
        # TODO Multiscale
        # TODO Shadow Shield (NOT IGNORABLE)
        if move.has_flag(MoveFlag.Sound) and target.has_ability(Ability.PunkRock):
            other_modifications *= 0.5
        if altered_move_type == PokemonType.Ghost and target.has_ability(
            Ability.PurifyingSalt
        ):
            attack *= 0.5
        if altered_move_type in [
            PokemonType.Ice,
            PokemonType.Fire,
        ] and target.has_ability(Ability.ThickFat):
            attack *= 0.5
        if altered_move_type == PokemonType.Fire and target.has_ability(
            Ability.WaterBubble
        ):
            other_modifications *= 0.5
        if move.category == MoveCategory.Special and target.has_ability(
            Ability.IceScales
        ):
            other_modifications *= 0.5

    # Unique mods
    if move.basePowerCallback:
        if move.name in ["Heavy Slam", "Heat Crash"]:
            power = heavy_slam(attacker.species.weightkg, target.species.weightkg)
        elif move.name == "Low Kick":
            power = low_kick(target.species.weightkg)
        elif move.name == "Electro Ball":
            power = electro_ball(attacker.stat(Stat.Speed), target.stat(Stat.Speed))
        else:
            logger.error("Didn't handle base power callback for %s", move.name)
    for type_, ability, multiplier in [
        (PokemonType.Grass, Ability.GrassySurge, 1.3),
        (PokemonType.Electric, Ability.ElectricSurge, 1.3),
        (PokemonType.Psychic, Ability.PsychicSurge, 1.3),
        (PokemonType.Fire, Ability.DesolateLand, 1.5),
        (PokemonType.Water, Ability.DesolateLand, 0),
        (PokemonType.Fire, Ability.Drought, 1.5),
        (PokemonType.Water, Ability.Drought, 0.5),
        (PokemonType.Fire, Ability.OrichalcumPulse, 1.5),
        (PokemonType.Electric, Ability.HadronEngine, 1.3),
        (PokemonType.Water, Ability.Drizzle, 1.5),
        (PokemonType.Water, Ability.PrimordialSea, 1.5),
        (PokemonType.Fire, Ability.PrimordialSea, 0),
        (PokemonType.Fairy, Ability.FairyAura, 1.33),
        (PokemonType.Dark, Ability.DarkAura, 1.33),
    ]:
        if altered_move_type == type_ and (
            attacker.has_ability(ability) or target.has_ability(ability)
        ):
            other_modifications *= multiplier
    if attacker.has_ability(Ability.DauntlessShield) and move.name == "Body Press":
        attack *= 1.5
    if offense_stat == Stat.Attack and attacker.has_ability(Ability.IntrepidSword):
        attack *= 1.5
    if defense_stat == Stat.Defence and target.has_ability(Ability.DauntlessShield):
        defence *= 1.5
    if offense_stat == Stat.SpecialAttack and attacker.has_ability(
        Ability.HadronEngine
    ):
        attack *= 1.33
    if offense_stat == Stat.Attack and attacker.has_ability(Ability.OrichalcumPulse):
        attack *= 1.33

    match move.multihit:
        case n if type(n) is int:
            nhits = n
        case n if type(n) is tuple[int, int]:
            nhits = n[1]
        case None:
            nhits = 1
        case _:
            assert False

    if altered_move_type in attacker.species.types:
        stab = 2 if attacker.has_ability(Ability.Adaptability) else 1.5
    else:
        stab = 1.0

    ### Type Effectiveness
    # TODO Scrappy
    # TODO Filter
    # TODO Prism Armor (NOT IGNORABLE)
    # TODO Friend Guard
    # TODO Solid Rock
    # TODO Wonder GUard

    type_multiplier = 1
    for poke_type in target.species.types:
        multiplier = TYPE_CHART[poke_type].get(altered_move_type, TypeMatchup.Neutral)
        if not (
            poke_type == PokemonType.Flying
            and target.has_ability(Ability.DeltaStream)
            and multiplier == TypeMatchup.SuperEffective
        ):
            type_multiplier *= multiplier

    logger.info(
        "Level %s, power %s, attack %s, defence %s", level, power, attack, defence
    )

    def final_formula(parental_bond=False):
        damage = math.floor(
            math.floor(math.floor(level * 2.0 / 5.0 + 2.0) * power * attack / defence)
            / 50.0
            + 2.0
        )  # From showdown, diverges from bulbapedia
        logger.info("Base damage: %s", damage)

        damage = pokemon_round(damage * target_multiplier)
        if parental_bond:
            damage = pokemon_round(damage * 0.25)
            logger.info("Parental bond second hit: %s", damage)
        # Weather
        # Glaive Rush
        if move.willCrit:
            damage = math.floor(damage * 1.5)
            logger.info("Crit: %s", damage)
        random = range(85, 101)
        damage = [math.floor(damage * r / 100) for r in random]
        logger.info("Range: %s", damage)
        damage = floored_multiply(
            damage, stab
        )  # From showdown, diverges from bulbapedia
        logger.info("Stab: %s", damage)
        damage = floored_multiply(damage, type_multiplier)
        logger.info("Type matchup: %s", damage)
        # BURN
        damage = pokerounded_multiply(damage, other_modifications)
        logger.info("Other: %s", damage)
        # ZMOVE
        # TERA SHIELD
        damage = pokerounded_multiply(damage, nhits)
        logger.info("Nhits: %s", damage)
        return damage

    damage = final_formula()
    if attacker.has_ability(Ability.ParentalBond) and not move.has_flag(
        MoveFlag.NoParentalBond
    ):
        second_hit = final_formula(True)
        damage = [damage[i] + second_hit[i] for i in range(len(damage))]
    return damage
