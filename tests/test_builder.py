import os.path
from typing import TypeVar

from layers.Builder import BaseBuilder, ContractBuilder, FunctionBuilder, VariableBuilder, MetadataBuilder
from layers.dataclass.Attributes import Mutability, Scope, Location, Visibility, Purity
from layers.dataclass.Components import Contract, Function, Variable

Buildable = TypeVar('Buildable', Contract, Function, Variable)
_target_code: str = """// SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0;contract ComplexChecks is A, B { using aa for *; uint256 public value; error ValueTooLow(uint256 provided, uint256 required);constructor(uint256 _initialValue) {      value = _initialValue;}function setValue(uint256 _value) public aa b(this) override {require(_value > 0, "Value must be greater than zero"); assert(value != _value); require(isEven(_value), "Value must be even"); if (_value < 10) {revert ValueTooLow({provided: _value, required: 10});} revert();     revert("This is a revert without a custom error"); value = _value;}function isEven(uint256 _value) internal pure returns (bool) {return _value % 2 == 0;}}"""
_cached = "49cd11d435ac68a380b5c14dd54b9720fa27bbd4250adb9b1136c7fa4673e784.sol"
_cached_path = BaseBuilder().loader.as_abs_path(os.path.join("out", _cached))


def test_metadata_builder():
    builder = MetadataBuilder()
    res = builder.build(_target_code)

    assert res.chain == "unichain"
    assert res.evm_version == "cancun"
    assert res.license == "MIT"
    assert res.solc_version == "0.8.0"


def test_contract_builder():
    builder = ContractBuilder()
    res = builder.build(_target_code)

    assert res.target_code == open(_cached_path, "r").read()
    assert res.inline_code != ""
    assert res.version == "0.8.0"
    assert res.name == "ComplexChecks"
    assert res.inheritance == ["A", "B"]
    assert res.library == ["aa"]


def test_function_builder():
    builder = FunctionBuilder()
    res = builder.build(_target_code)

    assert res[0].name == 'isEven'
    assert res[0].visibility == Visibility.INTERNAL
    assert res[0].parameters == ['uint256 _value']
    assert res[0].payable == False
    assert res[0].purity == Purity.PURE
    assert res[0].modifiers == []
    assert res[0].is_override == False
    assert res[0].returns == ['bool']
    assert res[0].body != ""

    assert res[1].name == 'setValue'
    assert res[1].visibility == Visibility.PUBLIC
    assert res[1].parameters == ['uint256 _value']
    assert res[1].payable == False
    assert res[1].purity is None
    assert res[1].modifiers == ['aa', 'b(this)']
    assert res[1].is_override == True
    assert res[1].returns == []
    assert res[1].body != ""


def test_variable_builder():
    builder = VariableBuilder()
    res = builder.build(_target_code)

    assert res[0].name == 'value'
    assert res[0].signature == 'ComplexChecks'
    assert res[0].type == 'uint256'
    assert res[0].location == Location.STORAGE
    assert res[0].visibility == Visibility.PUBLIC
    assert res[0].scope == Scope.STORAGE
    assert res[0].mutability == Mutability.MUTABLE

    assert res[1].name == '_value'
    assert res[1].signature == 'ComplexChecks:setValue'
    assert res[1].type == 'uint256'
    assert res[1].location == Location.MEMORY
    assert res[1].visibility is None
    assert res[1].scope == Scope.ARGS
    assert res[1].mutability == Mutability.MUTABLE

    assert res[2].name == '_value'
    assert res[2].signature == 'ComplexChecks:isEven'
    assert res[2].type == 'uint256'
    assert res[2].location == Location.MEMORY
    assert res[2].visibility is None
    assert res[2].scope == Scope.ARGS
    assert res[2].mutability == Mutability.MUTABLE
