from etherscan.ether_api_call import get_source_from_explorer


def test_a():
    output: str = get_source_from_explorer(
        "sepolia",
        "0xe8e23e97fa135823143d6b9cba9c699040d51f70"
    )  # Uniswap v4 PoolManager in sepolia
    print(output)
    assert len(output) >= 1
