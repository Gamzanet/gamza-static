from eth_typing import HexStr, HexAddress

from etherscan.ether_api_call import get_source_from_explorer


#    # (address,address,uint24,int24,address hookAddress) key
#    ("0x0000000000000000000000000000000000000000",
#    "0x6f0cd9ac99c852bdba06f72db93078cba80a32f5",
#    "0",
#    "60",
#    "0x7d61d057dd982b8b0a05a5871c7d40f8b96dd040")
#    # uint160 sqrtPriceX96
#    79228162514264337593543950336
#    # bytes hookData
#    0x
def get_sources_by_pool_key(currency0: str, currency1: str, hook: str):
    currency0_addr: HexAddress = to_hex_address(currency0)
    currency1_addr: HexAddress = to_hex_address(currency1)
    hook_addr: HexAddress = to_hex_address(hook)

    currency0_src = get_source_from_explorer(_network="unichain", _address=currency0_addr, use_cache=True)
    currency1_src = get_source_from_explorer(_network="unichain", _address=currency1_addr, use_cache=True)
    hook_src = get_source_from_explorer(_network="unichain", _address=hook_addr, use_cache=True)

    return currency0_src, currency1_src, hook_src


def to_hex_address(currency0: str) -> HexAddress:
    return HexAddress(HexStr(currency0))


if __name__ == "__main__":
    currency0 = "0x0000000000000000000000000000000000000000"
    currency1 = "0x6f0cd9ac99c852bdba06f72db93078cba80a32f5"
    fee = 0
    tickSpacing = 60
    hook = "0x7d61d057dd982b8b0a05a5871c7d40f8b96dd040"
    sqrtPriceX96 = 79228162514264337593543950336
    hookData = "0x"
    _srcs = get_sources_by_pool_key(currency0, currency1, hook)
    for src in _srcs:
        print(src)
