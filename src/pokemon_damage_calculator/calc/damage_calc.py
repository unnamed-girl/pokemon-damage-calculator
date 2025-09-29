from dataclasses import dataclass
import logging
import math

from pokemon_damage_calculator.calc.utils import (
    floored_multiply,
    pokemon_round,
    pokerounded_multiply,
)
from pokemon_damage_calculator.model.enums import (
    Ability,
    MoveCategory,
    MoveFlag,
    PokemonType,
    Status,
    Target,
)
from pokemon_damage_calculator.model.logic import (
    calc_base_power,
    calc_effective_attack,
    calc_effective_defence,
    calc_effective_power,
    calc_immunities,
    calc_move_type,
    calc_other_multipliers,
    calc_type_effectiveness,
)
from pokemon_damage_calculator.model.models import Move

from .pokemon import Pokemon

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .calcbuilder import GameState


logger = logging.getLogger()


@dataclass
class _MoveDetails:
    base_move: Move
    type: PokemonType
    ignores_ability: bool
    contact: bool
    crits: bool


def damage_calc(
    game_state: "GameState", attacker: Pokemon, target: Pokemon, move: Move
) -> list[int]:
    """
    Calculations as described in https://web.archive.org/web/20240516021936/https://www.trainertower.com/dawoblefets-damage-dissertation/.
    That is a gen 7 resource, my research into what is known about gen 9 differences will happen later.
    """
    if move.category == MoveCategory.Status:
        return [0]

    attacker_ignores_abilities = (
        move.ignoreAbility
        or attacker.has_ability(Ability.MoldBreaker)
        or attacker.has_ability(Ability.Turboblaze)
        or attacker.has_ability(Ability.Teravolt)
    )
    make_contact = move.has_flag(MoveFlag.Contact) and not attacker.has_ability(
        Ability.LongReach
    )

    crits = target.ability not in [Ability.BattleArmor, Ability.ShellArmor] and (
        move.willCrit
        or move.name in ["Storm Throw", "Frost Breath"]
        or attacker.ability == Ability.Merciless
        and target.status in [Status.Poison, Status.Toxic]
        # TODO Laser Focus or +3 crit chance
    )

    move_details = _MoveDetails(
        move,
        type=calc_move_type(attacker, target, move, game_state),
        ignores_ability=attacker_ignores_abilities,
        contact=make_contact,
        crits=crits,
    )

    base_power = calc_base_power(attacker, target, move, game_state)
    effective_power = calc_effective_power(
        attacker, target, move_details, game_state, base_power
    )
    effective_attack = calc_effective_attack(attacker, target, move_details, game_state)
    effective_defence = calc_effective_defence(
        attacker, target, move_details, game_state
    )
    attacker_level: int = attacker.level

    spread_multiplier = (
        1
        if not game_state.format.doubles
        or move.target
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

    weather_multiplier = game_state.weather.type_multiplier(move.type)

    # Exact values for crits are unknown as of gen 8
    crit_multiplier = 1.5 if move_details.crits else 1.0

    if move_details.type in attacker.species.types:
        stab_multiplier = 2 if attacker.has_ability(Ability.Adaptability) else 1.5
    else:
        stab_multiplier = 1.0

    type_effectiveness = calc_type_effectiveness(
        attacker, target, move_details, game_state
    )

    burn_multiplier = (
        0.5
        if (
            attacker.status == Status.Burn
            and move.category == MoveCategory.Physical
            and not attacker.ability == Ability.Guts
            and move.name != "Facade"
        )
        else 1.0
    )

    other_multiplier = calc_other_multipliers(
        attacker, target, move_details, game_state
    )

    # TODO Z-move ignores protect

    if calc_immunities(attacker, target, move_details, game_state, type_effectiveness):
        return [0 for _ in range(16)]

    # TODO following are etbs
    # if attacker.has_ability(Ability.DauntlessShield) and move.name == "Body Press":
    #     attack = math.floor(attack * 1.5)
    # if offense_stat == Stat.Attack and attacker.has_ability(Ability.IntrepidSword):
    #     attack = math.floor(attack * 1.5)
    # if defense_stat == Stat.Defence and target.has_ability(Ability.DauntlessShield):
    #     defence = math.floor(attack * 1.5)

    match move.multihit:
        case n if type(n) is int:
            nhits = n
        case n if type(n) is tuple[int, int]:
            nhits = n[1]
        case None:
            nhits = 1
        case _:
            assert False
    logger.info(
        """
        Attacker Level %s
        Effective Power %s
        Effective Attack %s
        Effective Defence %s
        Spread Multiplier %s
        weather_multiplier %s
        crit_multiplier %s
        type_effectiveness %s
        stab_multiplier %s
        burn_multiplier %s
        other_multiplier %s
        nhits %s
        """,
        attacker_level,
        effective_power,
        effective_attack,
        effective_defence,
        spread_multiplier,
        weather_multiplier,
        crit_multiplier,
        type_effectiveness,
        stab_multiplier,
        burn_multiplier,
        other_multiplier,
        nhits,
    )

    def final_formula(parental_bond: bool):
        damage = math.floor(
            math.floor(
                math.floor(attacker_level * 2.0 / 5.0 + 2.0)
                * effective_power
                * effective_attack
                / effective_defence
            )
            / 50.0
            + 2.0
        )  # From showdown, rounding diverges from bulbapedia
        logger.info("Base damage: %s", damage)

        damage = pokemon_round(damage * spread_multiplier)

        if parental_bond:
            damage = pokemon_round(damage * 0.25)

        damage = pokemon_round(damage * weather_multiplier)

        # Glaive Rush

        damage = pokemon_round(damage * crit_multiplier)

        damage = [math.floor(damage * r / 100) for r in range(85, 101)]

        damage = pokerounded_multiply(damage, stab_multiplier)

        damage = floored_multiply(damage, type_effectiveness)

        damage = pokerounded_multiply(damage, burn_multiplier)

        damage = pokerounded_multiply(damage, other_multiplier)

        # ZMOVE into prrotect
        # TERA SHIELD?

        damage = pokerounded_multiply(damage, nhits)

        damage = [max(1, d) for d in damage]
        damage = [d % 65536 for d in damage]
        return damage

    damage = final_formula(False)
    if attacker.has_ability(Ability.ParentalBond) and not move.has_flag(
        MoveFlag.NoParentalBond
    ):
        second_hit = final_formula(True)
        damage = [damage[i] + second_hit[i] for i in range(len(damage))]
    logger.info("Damage: %s", damage)
    return damage
