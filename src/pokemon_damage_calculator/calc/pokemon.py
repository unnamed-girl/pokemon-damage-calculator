import logging
import math

from pokemon_damage_calculator.data import get_nature, get_species
from pokemon_damage_calculator.model.enums import Ability, Stat
from pokemon_damage_calculator.model.models import Species
from pokemon_damage_calculator.model.natures import Nature, NatureModel
from ..model.models import StatDistribution

logger = logging.getLogger()


class Pokemon:
    def __init__(
        self,
        species: Species,
        ability=Ability.NoAbility,
        evs=StatDistribution.flat(),
        ivs=StatDistribution.flat(31),
        nature=get_nature("hardy"),
        level=50,
    ) -> None:
        self.species = species
        self.evs = evs
        self.nature = nature
        self.ability = ability
        self.ivs = ivs
        self.level = level

    def stat(self, stat: Stat) -> int:
        if self.nature.plus == stat:
            nature = 1.1
        elif self.nature.minus == stat:
            nature = 0.9
        else:
            nature = 1.0

        logger.info(
            "%s's %s nature is %s for %s", self.species.name, self.nature, nature, stat
        )
        logger.info("Ivs: %s and evs %s", self.ivs, self.evs)

        base_stat = self.species.baseStats[stat]
        ev = self.evs[stat]
        iv = self.ivs[stat]
        level = self.level

        if stat != Stat.HP:
            return math.floor(
                (
                    math.floor((2 * base_stat + iv + math.floor(ev / 4)) * level / 100)
                    + 5
                )
                * nature
            )
        else:
            return (
                math.floor((2 * base_stat + iv + math.floor(ev / 4)) * level / 100)
                + level
                + 10
            )

    def has_ability(self, ability: Ability) -> bool:
        return self.ability == ability


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
        self._level = 50

    def ev(self, stat: Stat, ev: int) -> "PokemonBuilder":
        self._evs[stat] = ev
        return self

    def iv(self, stat: Stat, iv: int) -> "PokemonBuilder":
        self._ivs[stat] = iv
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
            self._level,
        )
