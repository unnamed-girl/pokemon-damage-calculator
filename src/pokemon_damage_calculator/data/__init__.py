from typing import Optional
from serde import serde
from serde.json import from_json

from pokemon_damage_calculator.model.models import Move, Species
from pokemon_damage_calculator.model.models import NatureModel
from pokemon_damage_calculator.utils import clean_name

with open("data/pokedex.json") as f:
    _pokedex = from_json(dict[str, Species], f.read())

with open("data/moves.json") as f:
    _moves = from_json(dict[str, Move], f.read())

with open("data/natures.json") as f:
    _natures = from_json(dict[str, dict[str, NatureModel]], f.read())


@serde
class _Learnset:
    learnset: Optional[dict[str, list[str]]]
    eventdata: Optional[dict]

    def __repr__(self) -> str:
        return repr(self.learnset)


with open("data/learnsets.json") as f:
    _temp = from_json(dict[str, _Learnset], f.read())
    _learnsets = {
        pokemon: [_moves[move] for move in _temp[pokemon].learnset or {}]
        for pokemon in _temp
    }


def get_species(species_name: str) -> Species:
    return _pokedex[clean_name(species_name)]


def get_move(move_name: str) -> Move:
    return _moves[clean_name(move_name)]


def get_nature(nature_name: str) -> NatureModel:
    return _natures["9"][clean_name(nature_name)]


def get_learnset(species: "IntoSpecies") -> list[Move]:
    species = into_species(species)
    name = species.baseSpecies or species.name
    return _learnsets[clean_name(name)]


type IntoMove = Move | str


def into_move(move: IntoMove) -> Move:
    if isinstance(move, str):
        return get_move(move)
    elif isinstance(move, Move):
        return move


type IntoSpecies = Species | str


def into_species(species: IntoSpecies) -> Species:
    if isinstance(species, str):
        return get_species(species)
    elif isinstance(species, Species):
        return species
