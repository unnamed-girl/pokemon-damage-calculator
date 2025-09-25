from serde.json import from_json

from pokemon_damage_calculator.model.models import Move, Species
from pokemon_damage_calculator.model.natures import NatureModel
from pokemon_damage_calculator.utils import clean_name

with open("data/pokedex.json") as f:
    _pokedex = from_json(dict[str, Species], f.read())

with open("data/moves.json") as f:
    _moves = from_json(dict[str, Move], f.read())

with open("data/natures.json") as f:
    _natures = from_json(dict[str, dict[str, NatureModel]], f.read())


def get_species(species_name: str) -> Species:
    return _pokedex[clean_name(species_name)]


def get_move(move_name: str) -> Move:
    return _moves[clean_name(move_name)]


def get_nature(nature_name: str) -> NatureModel:
    return _natures["9"][clean_name(nature_name)]
