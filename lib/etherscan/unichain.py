"""
This module is used to fetch the source code of a contract from the Unichain network.
The source code is fetched from the Unichain Blockscout API and stored in the code/unichain directory.
"""

import os.path
from typing import TextIO

from eth_typing import HexAddress, HexStr

_network = "unichain"
_cache_base = os.path.join("code", _network)


def to_hex_address(_str: str) -> HexAddress:
    """
    Convert a string to a hex address
    :param _str: string address
    :return: hex address
    """
    return HexAddress(HexStr(_str))


def get_contract_json(_address: HexAddress) -> dict:
    """
    Get the source code of a contract
    :param _address: address of the contract
    :return: source code
    """
    _api_endpoint = "https://unichain-sepolia.blockscout.com/api/v2/smart-contracts/"
    import requests
    return requests.get(
        f"{_api_endpoint}{_address}",
        headers={"Content-Type": "application/json", "Cache-Control": "public"},
    ).json()


def store_all_dependencies(_address: str) -> list[str]:
    """
    Store all dependencies of a contract
    :param _address: address of the contract
    :return: paths where the source code is stored
    """
    _address = to_hex_address(_address)
    _file_path = os.path.join(_cache_base, "json", f"{_address}.json")

    # force cache, since no need to fetch the same contract source code multiple times
    import json
    try:
        with open(_file_path, "r") as j:
            _json = json.load(j)
    except FileNotFoundError:
        with open_with_mkdir(_file_path, "w") as j:
            _json = get_contract_json(_address)
            json.dump(_json, j)

    _keys = [_json["file_path"]]
    _sources = [_json["source_code"]]
    for s in _json["additional_sources"]:
        _keys.append(s["file_path"])
        _sources.append(s["source_code"])

    for i, s in enumerate(_sources):
        with open_with_mkdir(
            os.path.join(_cache_base, _keys[i]), "w"
        ) as j:
            j.write(s)
    return _keys


def open_with_mkdir(file_path: str, mode: str) -> TextIO:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return open(file_path, mode)


if __name__ == "__main__":
    address = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"  # Uniswap v4 PoolManager in unichain
    keys = store_all_dependencies(address)
    assert len(keys) > 0
