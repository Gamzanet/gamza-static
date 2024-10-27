from utils.unichain import store_all_dependencies


def test_store_all():
    address = "0x2880aB155794e7179c9eE2e38200202908C17B43"  # Pyth proxy contract in unichain
    keys = store_all_dependencies(address)
    assert len(keys) > 0
