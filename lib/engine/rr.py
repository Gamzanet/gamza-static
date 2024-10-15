import etherscan.unichain


def store_unichain_contract(_address: str) -> str:
    """
    Get the source unichain of an address.
    :param _address: The address to get the source unichain of.
    """
    etherscan.unichain.store_all_dependencies(_address)
