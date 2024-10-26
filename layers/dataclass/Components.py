from dataclasses import dataclass

from layers.dataclass.Attributes import Location, Visibility, Scope, Mutability


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
    # ... etc


# TODO: consider using slither classes

@dataclass
class Function(dict):
    name: str
    parameters: list[Variable]
    visibility: str
    modifiers: list[str]
    is_override: bool
    mutability: str
    returns: list[Variable]
    body: str
    _has_low_level_call: bool

    def has_low_level_call(self):
        raise NotImplementedError


# TODO: consider using slither classes


@dataclass(
    init=True,
    eq=True,
)
class Contract(dict):
    target_code: str
    version: str  # solc version # TODO: git commit hash if possible
    name: str
    inheritance: list[str]
    library: list[str]

    # modifier: list[str]
    # variable: list[Variable]
    # license: str
    # events: list[str]
    # structs: list[dict[str]]

    def is_valid_hook(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(f"{self.name}:{self.version}")


    @staticmethod
    def to_instance(data: dict) -> 'Contract':
        def skip_key_error(_key: str) -> any:
            try:
                return data.get(_key)
            except KeyError:
                return None

        return Contract(
            raw_code=skip_key_error('raw_code'),
            formatted_code=skip_key_error('formatted_code'),
            version=skip_key_error('version'),
            name=skip_key_error('name'),
            inheritance=skip_key_error('inheritance'),
            library=skip_key_error('library'),
            functions=skip_key_error('function'),
            modifier=skip_key_error('modifier'),
            variable=skip_key_error('variable'),
        )
