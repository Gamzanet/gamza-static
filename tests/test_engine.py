import os

import engine
import engine.foundry
import etherscan
import etherscan.unichain
import utils


def test_store_source_and_lint():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    _path = os.path.join("lib", "v4-core", "src", "PoolManager.sol")

    if not os.path.exists(_path):
        _path = etherscan.unichain.store_unichain_contract(_address)
        assert "PoolManager.sol" in _path

        etherscan.unichain.store_remappings(_address)
        etherscan.unichain.store_foundry_toml()
    [_stdout, _stderr] = engine.slither.lint_code(_path)
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
    _file = "ExampleHook.sol"
    _path = os.path.join(etherscan.foundry_dir, _file)
    with open(_path, "w") as f:
        f.write(dirty_code)

    # check if the source code not formatted
    diff = engine.foundry.format_code(_path)
    assert diff  # check if the source code successfully formatted


def test_forge_clone():
    # _address = "0x2880aB155794e7179c9eE2e38200202908C17B43"  # Pyth proxy contract in unichain
    # get contract dependencies
    pass


def test_set_solc_version():
    _expect = "0.8.28"
    _content = f"""// SPDX-License-Identifier: UNLICENSED
    pragma solidity >={_expect}; contract DoubleInitHook is BaseHook {{}}"""
    _version = engine.slither.set_solc_version_by_content(_content)
    assert _version == _expect
    engine.slither.set_solc_version(_version)
    _out = utils.paths.run_cli_must_succeed("solc-select versions", capture_output=True)
    assert f"{_expect} (current, set by" in _out
