import os

from engine import layer_0


def test_compile_slither():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    _path = layer_0.store_unichain_contract(_address)
    assert os.path.join("PoolManager.sol") in _path

    res: list[str] = layer_0.compile_slither(_path)
    print(res[0])  # stderr
    assert "INFO:Detectors:" in res[0]
