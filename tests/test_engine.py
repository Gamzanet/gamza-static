import os

from engine import layer_0
from etherscan import unichain


def test_compile_slither():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    _path = layer_0.store_unichain_contract(_address)
    assert os.path.join("PoolManager.sol") in _path

    layer_0.store_remappings(_address)
    layer_0.store_foundry_toml()

    res: list[str] = layer_0.lint_code(_path)
    print(res[0])  # stderr
    assert "INFO:Detectors:" in res[0]


def test_format():
    _address = "0x2880aB155794e7179c9eE2e38200202908C17B43"  # Pyth proxy contract in unichain
    # get contract dependencies
    _path = layer_0.store_unichain_contract(_address)
    print()
    print(_path)

    _file = os.path.join(unichain.foundry_dir, _path)
    assert open(_file).read()  # check if the source code successfully stored

    # check if the source code not formatted
    layer_0.format_code(_file)

    # format the source code
    # check if the source code formatted
    assert True


def test_lint():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    _path = layer_0.store_unichain_contract(_address)
    [_stdout, _stderr] = layer_0.lint_code(_path)
    assert "INFO:Detectors:" in _stdout
