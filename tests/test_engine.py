import os

from engine import layer_0
from etherscan import unichain


def test_store_source_and_lint():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"

    if not os.path.exists(unichain.foundry_dir):
        _path = layer_0.store_unichain_contract(_address)
        assert "PoolManager.sol" in _path

        layer_0.store_remappings(_address)
        layer_0.store_foundry_toml()
    else:
        _path = os.path.join("lib", "v4-core", "src", "PoolManager.sol")
    [_stdout, _stderr] = layer_0.lint_code(_path)
    assert "INFO:Detectors:" in _stdout


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
    _file = "ExampleHook.sol"
    _path = os.path.join(unichain.foundry_dir, _file)
    with open(_path, "w") as f:
        f.write(dirty_code)

    # check if the source code not formatted
    diff = layer_0.format_code(_path)
    assert diff  # check if the source code successfully formatted


def test_forge_clone():
    # _address = "0x2880aB155794e7179c9eE2e38200202908C17B43"  # Pyth proxy contract in unichain
    # get contract dependencies
    pass
