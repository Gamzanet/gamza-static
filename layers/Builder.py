import hashlib
import os
from dataclasses import dataclass

from jmespath import search

import lib.engine.layer_0
import lib.parser
from etherscan.unichain import get_contract_json, foundry_dir
from layers.dataclass.Components import Contract, Metadata, Function, Variable
from main import project_root
from parser.layer_2 import get_inheritance, get_library
from parser.run_semgrep import get_semgrep_output
from utils.paths import open_with_mkdir


@dataclass(
    init=True,
)
class Option(dict):
    target_code: str | None = None
    address: str | None = None
    lint_code: bool = False


@dataclass(
    init=True,
)
class BuildResult(dict):
    metadata: Metadata
    contract: Contract
    functions: list[Function]

    def items(self):
        return self.__dict__.items()


class Builder:
    def __init__(self, config: Option):
        # mutable options
        self.address = config.address
        self.target_code: str = config.target_code
        self.foundry_abs_path: str = os.path.join(project_root, foundry_dir)
        self.target_abs_path: str = os.path.join(self.foundry_abs_path, "raw.sol")

    @staticmethod
    def is_none(arg: str | None) -> bool:
        return arg is None or str(arg).strip() in ["", None]

    @staticmethod
    def metadata() -> Metadata:
        return Metadata(
            chain="unichain",
            evm_version="cancun"
        )

    def contract(self) -> Contract:
        raw_code: str = self.target_code
        formatted_code: str = lib.engine.layer_0.format_code(self.target_abs_path)
        version: str = lib.engine.layer_0.set_solc_version_by_content(raw_code)
        inheritance: list[str] = get_inheritance(self.target_abs_path)
        library: list[str] = get_library(self.target_abs_path)

        # $CONTRACT |&| $SIG |&| $VIS |&| $PAY |&| $PURITY |&| $MOD |&| $OVER |&| $RETURN |;|
        info_function = get_semgrep_output("info-function", self.target_abs_path)
        name: str = search("[0].data.CONTRACT", info_function)

        variable: list[Variable]
        return Contract(
            raw_code=raw_code,
            formatted_code=formatted_code,
            version=version,
            name=name,
            inheritance=inheritance,
            library=library,
        )

    def functions(self) -> list[Function]:
        functions: list[Function] = []
        # $CONTRACT |&| $SIG |&| $VIS |&| $PAY |&| $PURITY |&| $MOD |&| $OVER |&| $RETURN |;|
        info_function = get_semgrep_output("info-function", self.target_abs_path)
        # $CONTRACT |&| $SIG |&| $ARGS |&| $RETURNS |&| $IMPL |&| $TYPE |&| $LOCATION |&| $VISIBLE |&| $MUTABLE |&| $NAME |;|
        info_variable = get_semgrep_output("info-variable", self.target_abs_path)
        for f, v in zip(info_function, info_variable):
            continue
            functions.append(
                Function(
                    name=f["SIG"],
                    parameters=[Variable(
                        name=v["ARGS"],
                        type=v["TYPE"],
                        visibility=v["VISIBLE"],
                        mutability=v["MUTABLE"]
                    )],
                    visibility=f["VIS"],
                    modifiers=[f["MOD"]],
                    is_override=f["OVER"],
                    mutability=f["MUT"],
                    returns=[Variable(
                        name=v["RETURNS"],
                        type=v["TYPE"],
                        visibility=v["VISIBLE"],
                        mutability=v["MUTABLE"]
                    )],
                    body=f["IMPL"],
                    _has_low_level_call=False
                )
            )

        return functions

    def build(self) -> BuildResult:
        # 0. load remote code if not ready and store
        if self.is_none(self.target_code):
            self.target_code = self.get_remote_code()

        _file_hash = hashlib.sha3_224(self.target_code.encode()).hexdigest()
        self.target_abs_path = os.path.join(self.foundry_abs_path, f"{_file_hash}.sol")

        with open_with_mkdir(self.target_abs_path, "w") as f:
            f.write(self.target_code)

        # assume code ready and formatted: bubble up error
        # TODO: lint code (optional, here or in the next layer)
        return BuildResult(
            metadata=self.metadata(),
            contract=self.contract(),
            functions=self.functions()
        )

    def get_remote_code(self) -> str:
        if not self.is_none(self.address):
            if self.metadata().chain == "unichain":
                _json = get_contract_json(self.address)

                return _json["source_code"]
            raise NotImplementedError
        raise ValueError("No address provided")

    def code_ready(self):
        if not self.is_none(self.target_code):
            self.target_code = self.get_remote_code()
        # 1. format code

        # 2. lint code: can lint only if got code from remote
        raise NotImplementedError


def test_is_none():
    assert Builder.is_none("") is True
    assert Builder.is_none(None) is True
    assert Builder.is_none(" ") is True
    assert Builder.is_none("a") is False


def test_builder():
    builder = Builder(Option(
        target_code="""// SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;contract ComplexChecks is A, B { using aa for *; uint256 public value; error ValueTooLow(uint256 provided, uint256 required);constructor(uint256 _initialValue) {      value = _initialValue;}function setValue(uint256 _value) public {require(_value > 0, "Value must be greater than zero"); assert(value != _value); require(isEven(_value), "Value must be even"); if (_value < 10) {revert ValueTooLow({provided: _value, required: 10});} revert();     revert("This is a revert without a custom error"); value = _value;}function isEven(uint256 _value) internal pure returns (bool) {return _value % 2 == 0;}}""",
        lint_code=True,
        address="0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    ))
    assert builder.target_code != ""

    # metadata: Metadata
    # contract: Contract
    # functions: list[Function]
    res = builder.build()
    assert res.metadata.chain == "unichain"
    assert res.metadata.evm_version == "cancun"
    assert res.contract.raw_code != ""
    assert res.contract.formatted_code != ""
    assert res.contract.version == "0.8.0"
    assert res.contract.name == "ComplexChecks"
    assert res.contract.inheritance == ["A", "B"]
    assert res.contract.library == ["aa"]
    # assert res.functions != []
