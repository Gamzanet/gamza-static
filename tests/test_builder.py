import os.path
from typing import TypeVar

from layers.Builder import BaseBuilder, ContractBuilder, FunctionBuilder, VariableBuilder
from layers.dataclass.Attributes import Mutability, Scope, Location, Visibility
from layers.dataclass.Components import Contract, Function, Variable

Buildable = TypeVar('Buildable', Contract, Function, Variable)
_target_code: str = """// SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0;contract ComplexChecks is A, B { using aa for *; uint256 public value; error ValueTooLow(uint256 provided, uint256 required);constructor(uint256 _initialValue) {      value = _initialValue;}function setValue(uint256 _value) public aa b(this) override {require(_value > 0, "Value must be greater than zero"); assert(value != _value); require(isEven(_value), "Value must be even"); if (_value < 10) {revert ValueTooLow({provided: _value, required: 10});} revert();     revert("This is a revert without a custom error"); value = _value;}function isEven(uint256 _value) internal pure returns (bool) {return _value % 2 == 0;}}"""
_cached = "49cd11d435ac68a380b5c14dd54b9720fa27bbd4250adb9b1136c7fa4673e784.sol"
_cached_path = BaseBuilder().loader.as_abs_path(os.path.join("out", _cached))


def test_contract_builder():
    builder = ContractBuilder()
    assert builder.build(_target_code) == Contract(
        target_code=open(_cached_path, "r").read(),
        version="0.8.0",
        name="ComplexChecks",
        inheritance=["A", "B"],
        library=["aa"]
    )


def test_function_builder():
    builder = FunctionBuilder()
    assert builder.build(_target_code) == [
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
    assert builder.build(_target_code) == [
        Variable(name='value',
                 signature='ComplexChecks',
                 type='uint256',
                 location=Location.STORAGE,
                 visibility=Visibility.PUBLIC,
                 scope=Scope.STORAGE,
                 mutability=Mutability.MUTABLE),

        Variable(name='_value',
                 signature='ComplexChecks:setValue',
                 type='uint256',
                 location=Location.MEMORY,
                 visibility=None,
                 scope=Scope.ARGS,
                 mutability=Mutability.MUTABLE),

        Variable(name='_value',
                 signature='ComplexChecks:isEven',
                 type='uint256',
                 location=Location.MEMORY,
                 visibility=None,
                 scope=Scope.ARGS,
                 mutability=Mutability.MUTABLE)
    ]
