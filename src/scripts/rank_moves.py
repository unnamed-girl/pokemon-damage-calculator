from dataclasses import dataclass
from functools import total_ordering
from typing import Callable
from pokemon_damage_calculator.calc.calcbuilder import Format, IntoPokemon, into_pokemon
from pokemon_damage_calculator.calc.pokemon import PokemonBuilder
from pokemon_damage_calculator.data import IntoSpecies, get_learnset, into_species
from pokemon_damage_calculator.model.models import Move, StatDistribution


@dataclass
@total_ordering
class MoveRating:
    move: Move
    damage: list[int]

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, MoveRating):
            return False
        return self.damage == value.damage

    def __lt__(self, value: object) -> bool:
        if not isinstance(value, MoveRating):
            return False
        return self.damage < value.damage

    def __repr__(self) -> str:
        return f"{self.move}: {self.damage[0]}-{self.damage[-1]}"


def rate_moves(
    move_filter: Callable[[Move], bool], attacker: IntoPokemon, defender: IntoPokemon
) -> list[MoveRating]:
    attacker = into_pokemon(attacker)
    defender = into_pokemon(defender)

    learnset = get_learnset(attacker.species)
    game = Format.gen9vgc().game(attacker, defender)

    ratings = [
        MoveRating(move, game.calc(move)) for move in learnset if move_filter(move)
    ]

    return ratings


def matchup(
    move_filter: Callable[[Move], bool],
    static_pokemon: IntoPokemon,
    hypothetical_species: IntoSpecies,
):
    hypothetical_species = into_species(hypothetical_species)

    offence: list[MoveRating] = []
    defence: list[MoveRating] = []

    for ability in hypothetical_species.abilities.values():
        hypothetical = (
            PokemonBuilder(hypothetical_species)
            .evs(StatDistribution.flat(0))
            .ability(ability)
        )
        offence.extend(rate_moves(move_filter, static_pokemon, hypothetical))
        defence.extend(rate_moves(move_filter, hypothetical, static_pokemon))

    offence = list(
        {
            r.move.name: r
            for r in offence
            if not next(
                filter(lambda r2: r.move == r2.move and r2.damage < r.damage, offence),
                None,
            )
        }.values()
    )

    defence = list(
        {
            r.move.name: r
            for r in defence
            if not next(
                filter(lambda r2: r.move == r2.move and r2.damage > r.damage, defence),
                None,
            )
        }.values()
    )
    return (offence, defence)


if __name__ == "__main__":
    offence, defence = matchup(
        lambda move: move.is_normal(), PokemonBuilder("blastoisemega"), "blastoisemega"
    )

    offence.sort()
    defence.sort()

    print(offence[-5:])
    print(defence[-5:])
