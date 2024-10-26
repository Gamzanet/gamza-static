import hashlib
import os
from dataclasses import dataclass

from jmespath import search

import lib.engine.layer_0
import lib.parser
from etherscan.unichain import foundry_dir, get_contract_json
from layers.dataclass.Components import Contract, Metadata, Function, Variable
from main import project_root
from parser.run_semgrep import run_semgrep_one, get_semgrep_output
from utils.paths import open_with_mkdir


@dataclass
class Option:
    target_code: str
    lint_code: bool
    address: str = None  # optional

    def items(self):
        return self.__dict__.items()


@dataclass(
    init=True,
)
class BuildResult:
    metadata: Metadata
    contract: Contract
    functions: list[Function]


class Builder:
    def __init__(self, config: Option):
        # mutable options
        self.address = None
        self.target_code: str = ""
        self.foundry_abs_path: str = os.path.join(project_root, foundry_dir)
        self.target_abs_path: str = ""
        self.lint_code: bool = False
        for k, v in config.items():
            setattr(self, k, v)

    @staticmethod
    def is_none(option: str) -> bool:
        return str(option).strip() in ["", None]

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

        def get_inheritance():
            res = []
            info_inheritance: list[dict] = run_semgrep_one("info-inheritance", self.target_abs_path)
            for e in info_inheritance:  # $CONTRACT |&| $INHERIT |;|
                res.append(e["INHERIT"])
            return res

        inheritance: list[str] = get_inheritance()

        def get_library():
            res = []
            info_library: list[dict] = run_semgrep_one("info-library", self.target_abs_path)
            for e in info_library:
                res.append(e["LIBRARY"])
            return res

        library: list[str] = get_library()

        # $CONTRACT |&| $SIG |&| $VIS |&| $PAY |&| $PURITY |&| $MOD |&| $OVER |&| $RETURN |;|
        info_function = run_semgrep_one("info-function", self.target_abs_path)
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
        info_function = run_semgrep_one("info-function", self.target_abs_path)
        # $CONTRACT |&| $SIG |&| $ARGS |&| $RETURNS |&| $IMPL |&| $TYPE |&| $LOCATION |&| $VISIBLE |&| $MUTABLE |&| $NAME |;|
        info_variable = run_semgrep_one("info-variable", self.target_abs_path)
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

        return self.contract().functions

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
                return get_contract_json(self.address)["source_code"]
            raise NotImplementedError
        raise ValueError("No address provided")

    def code_ready(self):
        if not self.is_none(self.target_code):
            self.target_code = self.get_remote_code()
        # 1. format code

        # 2. lint code: can lint only if got code from remote
        raise NotImplementedError


def test_builder():
    builder = Builder(Option(
        target_code="""// SPDX-License-Identifier: MIT
        pragma solidity ^0.8.0;contract ComplexChecks { uint256 public value; error ValueTooLow(uint256 provided, uint256 required);constructor(uint256 _initialValue) {      value = _initialValue;}function setValue(uint256 _value) public {require(_value > 0, "Value must be greater than zero"); assert(value != _value); require(isEven(_value), "Value must be even"); if (_value < 10) {revert ValueTooLow({provided: _value, required: 10});} revert();     revert("This is a revert without a custom error"); value = _value;}function isEven(uint256 _value) internal pure returns (bool) {return _value % 2 == 0;}}""",
        lint_code=True,
    ))
    # print(builder.foundry_abs_path)

    # builder.code_ready()
    res = builder.build()
    print(res)


def test_info_inheritance():
    _code_rel_path = "code/2.sol"
    res = get_semgrep_output(
        "info-inheritance",
        _code_rel_path
    )
    assert (search("[*].data.INHERIT", res)
            == ["BaseHook", "someOtherContract"])
