from dataclasses import dataclass
from typing import Optional

from serde import field, serde

from pokemon_damage_calculator.model.enums import (
    Ability,
    BoostableStat,
    ContestType,
    IsNonStandard,
    MoveCategory,
    MoveFlag,
    MoveSelfDestructs,
    NonGhostTarget,
    PokemonType,
    PseudoWeather,
    SideCondition,
    Stat,
    Status,
    Target,
    Terrain,
    UniqueDamage,
    UniqueOHKO,
    UniqueOffensivePokemon,
    UniqueSelfSwitch,
    UniqueSlotCondition,
    VolatileStatus,
    Weather,
)


@serde
class StatDistribution:
    hp: int
    atk: int
    def_: int = field(rename="def")
    spa: int
    spd: int
    spe: int

    def __getitem__(self, index: Stat) -> int:
        if index == Stat.Defence:
            return self.def_
        else:
            return getattr(self, index.value)

    def __setitem__(self, index: Stat, value: int):
        if index == Stat.Defence:
            self.def_ = value
        else:
            setattr(self, index.value, value)

    @staticmethod
    def flat(n=0) -> "StatDistribution":
        return StatDistribution(hp=n, atk=n, def_=n, spa=n, spd=n, spe=n)

    @classmethod
    def manual(cls, hp=0, atk=0, def_=0, spa=0, spd=0, spe=0) -> "StatDistribution":
        return StatDistribution(hp=hp, atk=atk, def_=def_, spa=spa, spd=spd, spe=spe)


@serde
class Species:
    name: str
    types: list[PokemonType]
    baseStats: StatDistribution
    abilities: dict[str, Ability]
    baseSpecies: Optional[str]
    weightkg: int | float

    def __repr__(self) -> str:
        return f"<{self.name}>"


@dataclass(kw_only=True)  # shuts up pylance, TODO fix this
@serde
@dataclass(kw_only=True)
class Move:
    num: int
    accuracy: int | bool
    basePower: int
    category: MoveCategory
    isNonstandard: Optional[IsNonStandard]
    name: str
    pp: int
    priority: int
    flags: list[MoveFlag]  # enum not comprehensive
    isZ: Optional[str]
    critRatio: Optional[int]
    secondary: dict | None
    target: Target
    type: PokemonType
    contestType: ContestType | None
    desc: str | None
    shortDesc: str | None
    drain: tuple[int, int] | None
    boosts: dict[BoostableStat, int] | None
    zMove: dict | None  # TODO inner structure
    basePowerCallback: bool = field(default=False)
    condition: dict | None  # TODO inner structure
    volatileStatus: VolatileStatus | None
    multihit: tuple[int, int] | int | None
    callsMove: bool = field(default=False)
    sideCondition: SideCondition | None
    hasCrashDamage: bool = field(default=False)
    stallingMove: bool = field(default=False)
    selfSwitch: UniqueSelfSwitch | bool = field(default=False)
    ignoreImmunity: bool | dict[PokemonType, bool] = field(default=False)
    overrideOffensiveStat: Stat | None
    # maxMove: dict  # TODO inner structure
    recoil: tuple[int, int] | None = None
    weather: Weather | None
    ignoreDefensive: bool = field(default=False)
    ignoreEvasion: bool = field(default=False)
    forceSwitch: bool = field(default=False)
    # selfBoost: dict  # TODO inner structure
    nonGhostTarget: NonGhostTarget | None = None
    status: Status | None = None
    smartTarget: bool = field(default=False)
    damage: UniqueDamage | int | None = None
    terrain: Terrain | None = None
    hasSheerForce: bool = field(default=False)
    selfdestruct: MoveSelfDestructs | None = None
    pseudoWeather: PseudoWeather | None = None
    onDamagePriority: int | None = None
    breaksProtect: bool = field(default=False)
    secondaries: list[dict] | None  # TODO: inner structure
    ohko: UniqueOHKO | bool = field(default=False)
    willCrit: bool = field(default=False)
    overrideOffensivePokemon: UniqueOffensivePokemon | None = None
    isMax: bool | str | None = None
    ignoreAbility: bool = field(default=False)
    slotCondition: UniqueSlotCondition | None = None
    heal: tuple[int, int] | None = None
    realMove: str | None = None
    thawsTarget: bool = field(default=False)
    mindBlownRecoil: bool = field(default=False)
    multiaccuracy: bool = field(default=False)
    overrideDefensiveStat: Stat | None = None
    noPPBoosts: bool = field(default=False)
    sleepUsable: bool = field(default=False)
    tracksTarget: bool = field(default=False)
    stealsBoosts: bool = field(default=False)
    struggleRecoil: bool = field(default=False)

    def __init__(self, **kwargs) -> None:
        self.__dict__ = kwargs

    @classmethod
    def load_json(cls, data) -> "Move":
        data["flags"] = data["flags"].keys()
        result = Move(**data)
        return result

    def has_flag(self, flag: MoveFlag) -> bool:
        return flag in self.flags

    def is_normal(self) -> bool:
        if self.selfdestruct:
            return False
        if self.name in ["Dream Eater", "Belch"]:
            return False
        if self.condition and "duration" in self.condition:
            return False
        for flag in [MoveFlag.Recharge, MoveFlag.Charge, MoveFlag.FutureMove]:
            if flag in self.flags:
                return False
        if isinstance(self.accuracy, int):
            if self.accuracy <= 50:
                return False
        return True

    @classmethod
    def generic_move(cls, power: int, category: MoveCategory) -> "Move":
        return Move(
            name="GENERIC",
            basePower=power,
            category=category,
            type=PokemonType.Unknown,
            accuracy=100,
        )

    def __repr__(self) -> str:
        return f"<{self.name}>"


@serde(deny_unknown_fields=True)
class NatureModel:
    name: str
    _plus: Stat | None = field(rename="plus")
    _minus: Stat | None = field(rename="minus")

    def increases(self, stat: Stat) -> bool:
        return stat == self._plus

    def decreases(self, stat: Stat) -> bool:
        return stat == self._minus
