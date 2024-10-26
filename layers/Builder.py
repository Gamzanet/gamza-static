import os.path
from typing import Generic, TypeVar

from engine.layer_0 import set_solc_version_by_content
from layers.Loader import Loader
from layers.dataclass.Attributes import Mutability, Scope, Location, Visibility
from layers.dataclass.Components import Contract, Function, Variable
from parser.layer_2 import get_inheritance, get_library, get_contract_name, get_variables

Buildable = TypeVar('Buildable', Contract, Function, Variable)


class BaseBuilder(Generic[Buildable]):
    def __init__(self):
        self.loader = Loader()

    def build(self, _code) -> str:
        _path = self.loader.cache_content(_code, "sol")
        if not os.path.exists(_path):
            _path = self.loader.cache_content(_code, "sol")
        self.loader.format(_path)
        return _path


class ContractBuilder(BaseBuilder[Contract]):
    def __init__(self):
        super().__init__()

    def build(self, _code) -> Contract:
        _path = super().build(_code)
        _code = self.loader.read_code(_path)
        _version = set_solc_version_by_content(_code)
        return Contract(
            target_code=_code,
            version=_version,
            name=get_contract_name(_path),
            inheritance=get_inheritance(_path),
            library=get_library(_path)
        )


class FunctionBuilder(BaseBuilder[Function]):
    def __init__(self):
        super().__init__()

    def build(self, _code) -> list[Function]:
        _path = super().build(_code)
        return FunctionBuilder.mock()

    @staticmethod
    def mock() -> list[Function]:
        return [
            Function(
                name="setValue",
                parameters=[],
                visibility="public",
                modifiers=["aa", "b(this)"],
                is_override=True,
                mutability="",
                returns=[],
                body="""
                    require(_value > 0, "Value must be greater than zero");
                    assert(value != _value);
                    require(isEven(_value), "Value must be even");
                    if (_value < 10) {
                        revert ValueTooLow({provided: _value, required: 10});
                    }
                    revert();
                    revert("This is a revert without a custom error");
                    value = _value;""".strip(),
                _has_low_level_call=True
            ),
            Function(
                name="isEven",
                parameters=[],
                visibility="internal",
                modifiers=[],
                is_override=False,
                mutability="pure",
                returns=[],
                body="return _value % 2 == 0;",
                _has_low_level_call=False
            )
        ]


class VariableBuilder(BaseBuilder[Variable]):
    def __init__(self):
        super().__init__()

    def build(self, _code) -> list[Variable]:
        _path = super().build(_code)
        # 1. Parser should extract the variables
        _parsed = get_variables(_path)
        # 2. Builder should build the variables
        res = []
        for _name, _variables in _parsed.items():
            for _variable in _variables:
                res.append(
                    Variable(
                        name=_variable["NAME"],
                        signature=_variable["SIG"],
                        type=_variable["TYPE"],
                        location=Location.from_str(_variable["LOCATION"]),
                        visibility=Visibility.from_str(_variable["VISIBLE"]),
                        scope=Scope.from_str(_variable["SCOPE"]),
                        mutability=Mutability.from_str(_variable["MUTABLE"])
                    )
                )
        return res

    @staticmethod
    def mock() -> list[Variable]:
        return [
            Variable(
                name="value",
                signature="ComplexChecks",
                type="uint256",
                location=Location.STORAGE,
                visibility=Visibility.PUBLIC,
                scope=Scope.STORAGE,
                mutability=Mutability.MUTABLE
            ),
            Variable(
                name="_value",
                signature="ComplexChecks:setValue",
                type="bytes",
                location=Location.CALLDATA,
                visibility=Visibility.PUBLIC,
                scope=Scope.ARGS,
                mutability=Mutability.IMMUTABLE
            ),
            Variable(
                name="result",
                signature="ComplexChecks:setValue",
                type="bytes",
                location=Location.MEMORY,
                visibility=Visibility.INTERNAL,
                scope=Scope.RETURNS,
                mutability=Mutability.MUTABLE
            ),
            Variable(
                name="_value",
                signature="ComplexChecks:isEven",
                type="uint256",
                location=Location.MEMORY,
                visibility=Visibility.INTERNAL,
                scope=Scope.ARGS,
                mutability=Mutability.MUTABLE
            ),
            Variable(
                name="result",
                signature="ComplexChecks:isEven",
                type="bool",
                location=Location.MEMORY,
                visibility=Visibility.INTERNAL,
                scope=Scope.RETURNS,
                mutability=Mutability.MUTABLE
            )
        ]
