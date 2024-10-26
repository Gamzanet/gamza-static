from typing import Generic, TypeVar

from engine.layer_0 import set_solc_version_by_content
from layers.Loader import Loader
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

    def build(self, code) -> Function:
        raise NotImplementedError


class VariableBuilder(BaseBuilder[Variable]):
    def __init__(self):
        super().__init__()

    def build(self, code) -> Variable:
        raise NotImplementedError


def test_contract_builder():
    target_code: str = """// SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0;contract ComplexChecks is A, B { using aa for *; uint256 public value; error ValueTooLow(uint256 provided, uint256 required);constructor(uint256 _initialValue) {      value = _initialValue;}function setValue(uint256 _value) public {require(_value > 0, "Value must be greater than zero"); assert(value != _value); require(isEven(_value), "Value must be even"); if (_value < 10) {revert ValueTooLow({provided: _value, required: 10});} revert();     revert("This is a revert without a custom error"); value = _value;}function isEven(uint256 _value) internal pure returns (bool) {return _value % 2 == 0;}}"""
    builder = ContractBuilder()
    _path = builder.loader.cache_content(target_code, "sol")
    build = builder.build(_path)
    assert build.target_code == target_code
    assert build.version == "0.8.0"
    assert build.name == "ComplexChecks"
    assert build.inheritance == ["A", "B"]
    assert build.library == ["aa"]
    assert build == Contract(
        target_code=target_code,
        version="0.8.0",
        name="ComplexChecks",
        inheritance=["A", "B"],
        library=["aa"]
    )
