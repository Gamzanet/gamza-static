import os.path
from typing import Generic, TypeVar

from engine.layer_0 import set_solc_version_by_content
from layers.Loader import Loader
from layers.dataclass.Attributes import Mutability, Scope, Location, Visibility
from layers.dataclass.Components import Contract, Function, Variable
from parser.layer_2 import get_inheritance, get_library, get_contract_name

Buildable = TypeVar('Buildable', Contract, Function, Variable)


class BaseBuilder(Generic[Buildable]):
    def __init__(self):
        self.loader = Loader()

    def build(self, code) -> Buildable:
        raise NotImplementedError("Method not implemented")


class ContractBuilder(BaseBuilder[Contract]):
    def __init__(self):
        super().__init__()

    def build(self, _path) -> Contract:
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

    def build(self, code) -> list[Function]:
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

    def build(self, code) -> list[Variable]:
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


_target_code: str = """// SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0;contract ComplexChecks is A, B { using aa for *; uint256 public value; error ValueTooLow(uint256 provided, uint256 required);constructor(uint256 _initialValue) {      value = _initialValue;}function setValue(uint256 _value) public aa b(this) override {require(_value > 0, "Value must be greater than zero"); assert(value != _value); require(isEven(_value), "Value must be even"); if (_value < 10) {revert ValueTooLow({provided: _value, required: 10});} revert();     revert("This is a revert without a custom error"); value = _value;}function isEven(uint256 _value) internal pure returns (bool) {return _value % 2 == 0;}}"""
_cached = "49cd11d435ac68a380b5c14dd54b9720fa27bbd4250adb9b1136c7fa4673e784.sol"
_cached_path = BaseBuilder().loader.as_abs_path(os.path.join("out", _cached))


def test_contract_builder():
    builder = ContractBuilder()
    _path = _cached_path
    if not os.path.exists(_path):
        _path = builder.loader.cache_content(_target_code, "sol")
    assert builder.build(_path) == Contract(
        target_code=_target_code,
        version="0.8.0",
        name="ComplexChecks",
        inheritance=["A", "B"],
        library=["aa"]
    )


def test_function_builder():
    builder = FunctionBuilder()
    _path = _cached_path
    if not os.path.exists(_path):
        _path = builder.loader.cache_content(_target_code, "sol")
    assert builder.build(_path) == [
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


def test_variable_builder():
    builder = VariableBuilder()
    _path = _cached_path
    if not os.path.exists(_path):
        _path = builder.loader.cache_content(_target_code, "sol")
    assert builder.build(_path) == [
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
