import hashlib

import attr
import attrs

from layers.dataclass.Attributes import Location, Visibility, Scope, Mutability, Purity, Condition


# TODO: consider using slither classes

@attr.s(auto_attribs=True)
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

@attr.s(auto_attribs=True)
class Metadata(dict):
    chain: str
    evm_version: str
    license: str
    solc_version: str
    # ... etc


@attr.s(auto_attribs=True)
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
    access_control: list[Condition]

    # _has_low_level_call: bool

    def has_low_level_call(self):
        raise NotImplementedError

    def items(self):
        return self.__dict__.items()


@attr.s(auto_attribs=True)
class Contract(dict):
    target_code: str
    imports: list[str]
    inline_code: str
    name: str
    inheritance: list[str]
    library: list[str]

    def is_valid_hook(self):
        raise NotImplementedError

    def __hash__(self):
        return hash(f"{self.name}:{hashlib.sha3_256(self.inline_code.encode()).hexdigest()[0:8]}")


@attr.s(auto_attribs=True)
class ResultScope:
    name: str
    variable: list[Variable]


@attr.s(auto_attribs=True)
class ContractScope(ResultScope):
    functions: list[str]
    libraries: list[str]


@attr.s(auto_attribs=True)
class FunctionScope(ResultScope):
    parameters: list[Variable]
    purity: Purity
    visibility: Visibility
    payable: bool
    override: bool
    modifier: list[str]
    returns: list[Variable]
    body: str
    access_control: list[Condition]


@attr.s(auto_attribs=True)
class FileScope:
    file_name: str
    license: str
    solc_version: str
    imports: list[str]
    contract_scope: ContractScope
    function_scopes: list[FunctionScope]


@attrs.define(init=True, auto_attribs=True)
class DetectionLog:
    title: any
    summary: str
    description: str
    impact: str
    severity: str
    recommendation: str | None
    scopes: list[FileScope | ContractScope | FunctionScope]


@attrs.frozen(auto_attribs=True)
class SlitherData:
    description: str
    impact: str


@attrs.frozen(auto_attribs=True)
class SimpleDetectionLog:
    detector: str
    data: SlitherData

    @staticmethod
    def from_log(log: DetectionLog):
        return SimpleDetectionLog(
            detector=log.summary,
            data=SlitherData(
                description=log.description,
                impact=log.impact
            )
        )
