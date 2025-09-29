from dataclasses import dataclass
from functools import total_ordering
from typing import Callable, Iterable
from pokemon_damage_calculator.calc.calcbuilder import Format, IntoPokemon, into_pokemon
from pokemon_damage_calculator.calc.pokemon import Pokemon, PokemonBuilder
from pokemon_damage_calculator.data import (
    IntoSpecies,
    get_learnset,
    get_species,
    into_species,
)
from pokemon_damage_calculator.model.enums import Ability, Stat
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
    
@dataclass
@total_ordering
class MoveRatingList:
    move: Move
    damage: list[list[int]]

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, MoveRating):
            return False
        assert len(value.damage) == len(self.damage)
        return self.damage == value.damage

    def __lt__(self, value: object) -> bool:
        if not isinstance(value, MoveRatingList):
            return False
        assert len(value.damage) == len(self.damage)
        return self.damage[0][0] < value.damage[0][0]

    def __repr__(self) -> str:
        ranges = "-".join(str(d[-1]) for d in self.damage)
        return f"{self.move}: {ranges}"



def rate_moves(attacker: IntoPokemon, defender: IntoPokemon) -> list[MoveRating]:
    attacker = into_pokemon(attacker)
    defender = into_pokemon(defender)

    learnset = get_learnset(attacker.species)
    game = Format.gen9vgc().game(attacker, defender)

    ratings = [MoveRating(move, game.calc(move)) for move in learnset]

    return ratings

def vary_evs[T](
    evs: Iterable[StatDistribution], next_func: Callable[[PokemonBuilder], T]
) -> Callable[[PokemonBuilder], list[T]]:
    def inner(pokemon: PokemonBuilder) -> list[T]:
        result: list[T] = []
        for spread in evs:
            result.append(next_func(pokemon.evs(spread)))
        return result
    return inner


def vary_ability[T](
    next_func: Callable[[PokemonBuilder], T],
) -> Callable[[PokemonBuilder], dict[Ability, T]]:
    def inner(pokemon: PokemonBuilder) -> dict[Ability, T]:
        result: dict[Ability, T] = {}
        for ability in pokemon._species.abilities.values():
            result[ability] = next_func(pokemon.ability(ability))
        return result

    return inner


def constant_pokemon(
    my_pokemon: IntoPokemon,
) -> Callable[[PokemonBuilder], tuple[list[MoveRating], list[MoveRating]]]:
    def inner(pokemon: PokemonBuilder) -> tuple[list[MoveRating], list[MoveRating]]:
        return (rate_moves(my_pokemon, pokemon), rate_moves(pokemon, my_pokemon))

    return inner

def list_movewise(spreadwise: list[tuple[list[MoveRating], list[MoveRating]]]) -> tuple[list[MoveRatingList], list[MoveRatingList]]:
    movewise_offence: dict[str, MoveRatingList] = {}
    movewise_defence: dict[str, MoveRatingList] = {}
    for offence, defence in spreadwise:
        for rating in offence:
            movewise_offence.setdefault(rating.move.name, MoveRatingList(rating.move, []))
            movewise_offence[rating.move.name].damage.append(rating.damage)
        for rating in defence:
            movewise_defence.setdefault(rating.move.name,  MoveRatingList(rating.move, []))
            movewise_defence[rating.move.name].damage.append(rating.damage)
    return (list(movewise_offence.values()), list(movewise_defence.values()))

if __name__ == "__main__":
    matchups = vary_ability(
    vary_evs(
        [StatDistribution.flat(), StatDistribution.flat(252)],
        constant_pokemon(PokemonBuilder("malamar")),
    ))(PokemonBuilder("ironvaliant"))

    for ability, spreads in matchups.items():
        offence, defence = list_movewise(spreads)
        offence.sort()
        defence.sort()

        print(f"{ability}:")
        print(f"Offence: {", ".join(str(r) for r in offence[-5:])}")
        print(f"Defence: {", ".join(str(r) for r in defence[-5:])}")