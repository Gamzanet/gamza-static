from engine.rr import store_unichain_contract


def test_make_foundry():
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    store_unichain_contract(_address)
