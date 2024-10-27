import os

from engine.foundry import format_code
from engine.slither import set_solc_version_by_content, lint_code, set_solc_version
from etherscan.unichain import store_unichain_contract, store_remappings, store_foundry_toml
from layers.Loader import Loader
from utils.paths import run_cli_must_succeed


def test_store_source_and_lint():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    _path = os.path.join("lib", "v4-core", "src", "PoolManager.sol")

    if not os.path.exists(_path):
        _path = store_unichain_contract(_address)
        assert "PoolManager.sol" in _path

        store_remappings(_address)
        store_foundry_toml()
    [_stdout, _stderr] = lint_code(_path)
    assert "INFO:Detectors:" in _stderr
    print(_stdout, _stderr)


def test_format():
    dirty_code = """// SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;contract ExampleHook is BaseHook,
    someOtherContract {function getHookPermissions()public pure
    override returns (Hooks.Permissions memory){return
    Hooks.Permissions({beforeInitialize: true,afterInitialize: true,
    beforeSwap: false,afterSwap: true,beforeAddLiquidity: true,
    afterAddLiquidity: true,beforeRemoveLiquidity: true,
    afterRemoveLiquidity: true,beforeDonate: true,afterDonate: true
    });}}"""
    _path = Loader().cache_content(
        dirty_code, "sol"
    )

    # check if the source code not formatted
    diff = format_code(_path)
    assert diff  # check if the source code successfully formatted


def test_set_solc_version():
    _expect = "0.8.28"
    _content = f"""// SPDX-License-Identifier: UNLICENSED
    pragma solidity >={_expect}; contract DoubleInitHook is BaseHook {{}}"""
    _version = set_solc_version_by_content(_content)
    assert _version == _expect
    set_solc_version(_version)
    _out = run_cli_must_succeed("solc-select versions", capture_output=True)
    assert f"{_expect} (current, set by" in _out
