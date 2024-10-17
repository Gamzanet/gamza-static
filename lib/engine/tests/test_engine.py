import os

from engine.layer_0 import store_unichain_contract, compile_slither


def test_compile_slither():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    _path = store_unichain_contract(_address)
    assert os.path.join("PoolManager.sol") in _path

    res: list[str] = compile_slither(_path)
    print(res[0])  # stderr
    assert "INFO:Detectors:" in res[0]
