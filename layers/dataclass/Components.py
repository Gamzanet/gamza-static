from dataclasses import dataclass

from layers.dataclass.Attributes import Location, Visibility, Scope, Mutability, Purity


# TODO: consider using slither classes

@dataclass
class Variable(dict):
    name: str
    signature: str  # contract:(function)
    type: str
    location: Location  # memory, storage, calldata, transient
    visibility: Visibility | None  # external, public, internal, private
    # visibility is None only if a variable implicitly defined in args and returns
    scope: Scope  # function, storage, args, returns, inherited
    mutability: Mutability  # mutable, immutable, constant, transient


# TODO: map library and inheritance to mappings of import path

@dataclass(
    init=True,
    frozen=True,
)
class Metadata(dict):
    chain: str
    evm_version: str
    license: str
    solc_version: str
    # ... etc


@dataclass
class Function(dict):
    name: str | None
    parameters: list[str]
    visibility: Visibility
    modifiers: list[str]
    is_override: bool
    payable: bool
    purity: Purity | None
    returns: list[str] | None
    body: str

    # _has_low_level_call: bool

    def has_low_level_call(self):
        raise NotImplementedError

    def items(self):
        return self.__dict__.items()


@dataclass(
    init=True,
    eq=True,
)
class Contract(dict):
    target_code: str
    inline_code: str
    version: str  # solc version # TODO: git commit hash if possible
    name: str
    inheritance: list[str]
    library: list[str]

    def is_valid_hook(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(f"{self.name}:{self.version}")
