import logging
import math
from typing import Optional, TYPE_CHECKING

from pokemon_damage_calculator.data import get_nature, get_species
from pokemon_damage_calculator.model.enums import Ability, PokemonType, Stat, Status
from pokemon_damage_calculator.model.logic import stat_modifications
from pokemon_damage_calculator.model.models import Species
from pokemon_damage_calculator.model.natures import Nature, NatureModel
from ..model.models import StatDistribution

if TYPE_CHECKING:
    from pokemon_damage_calculator.calc.calcbuilder import GameState

logger = logging.getLogger()


class Pokemon:
    def __init__(
        self,
        species: Species,
        ability=Ability.NoAbility,
        evs=StatDistribution.flat(),
        ivs=StatDistribution.flat(31),
        nature=get_nature("hardy"),
        item=None,
        level=50,
    ) -> None:
        self.species = species
        self.evs = evs
        self.nature = nature
        self.ability = ability
        self.ivs = ivs
        self.level = level
        self.status: Optional[Status] = None
        self.current_hp = self.raw_stat(Stat.HP)
        self.item = item
        self.boosts = StatDistribution.flat()

    def raw_stat(self, stat: Stat) -> int:
        if self.nature.plus == stat:
            nature = 1.1
        elif self.nature.minus == stat:
            nature = 0.9
        else:
            nature = 1.0

        base = self.species.baseStats[stat]
        ev = self.evs[stat]
        iv = self.ivs[stat]
        level = self.level

        if stat != Stat.HP:
            return math.floor(
                (math.floor((2 * base + iv + math.floor(ev / 4)) * level / 100) + 5)
                * nature
            )
        else:
            return (
                math.floor((2 * base + iv + math.floor(ev / 4)) * level / 100)
                + level
                + 10
            )
    def boost_fraction(self, stat: Stat) -> float:
        numerator = max(2, 2 + self.boosts[stat])
        denominator = max(2, 2 - self.boosts[stat])
        return numerator/denominator
    def stat(self, stat: Stat, game_state: "GameState") -> int:
        raw_stat = self.raw_stat(stat)
        result = stat_modifications(self, game_state, stat, raw_stat)
        result = math.floor(result * self.boost_fraction(stat))
        logger.info(
            "Species %s's %s is %s",
            self.species.name,
            stat,
            result,
        )
        return result

    def has_ability(self, ability: Ability) -> bool:
        return self.ability == ability

    def get_types(self) -> list[PokemonType]:
        return self.species.types

    def is_grounded(self, ability_ignored: bool) -> bool:
        if PokemonType.Flying in self.get_types() or (
            not ability_ignored and self.ability == Ability.Levitate
        ):
            return False
        # TODO Air Balloon
        # TODO Magnet Rise and Telekinesis
        # TODO Iron Ball
        # TODO Ingrain, Smack Down, Thousand Arrows
        # TODO Gravity
        # TODO Roost
        return True


class PokemonBuilder:
    def __init__(self, species: Species | str) -> None:
        if type(species) is str:
            self._species = get_species(species)
        elif type(species) is Species:
            self._species = species
        else:
            assert False

        self._evs = StatDistribution.flat()
        self._ivs = StatDistribution.flat(31)
        self._nature = get_nature(Nature.HARDY)
        self._ability = Ability.NoAbility
        self._item = None
        self._level = 50

    def ev(self, stat: Stat, ev: int) -> "PokemonBuilder":
        self._evs[stat] = ev
        return self

    def evs(self, distribution: StatDistribution) -> "PokemonBuilder":
        self._evs = distribution
        return self

    def ability(self, ability: Ability) -> "PokemonBuilder":
        self._ability = ability
        return self

    def iv(self, stat: Stat, iv: int) -> "PokemonBuilder":
        self._ivs[stat] = iv
        return self

    def ivs(self, distribution: StatDistribution) -> "PokemonBuilder":
        self._ivs = distribution
        return self

    def nature(self, nature: NatureModel | Nature) -> "PokemonBuilder":
        if type(nature) is Nature:
            self._nature = get_nature(nature)
        elif type(nature) is NatureModel:
            self._nature = nature
        return self

    def level(self, level: int) -> "PokemonBuilder":
        self._level = level
        return self

    def build(self) -> Pokemon:
        return Pokemon(
            self._species,
            self._ability,
            self._evs,
            self._ivs,
            self._nature,
            self._item,
            self._level,
        )


type IntoPokemon = Pokemon | PokemonBuilder


def into_pokemon(pokemon: IntoPokemon) -> Pokemon:
    if type(pokemon) is PokemonBuilder:
        return pokemon.build()
    elif type(pokemon) is Pokemon:
        return pokemon
    else:
        assert False
