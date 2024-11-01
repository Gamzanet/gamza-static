"""
This module is used to fetch the source code of a contract from the Unichain network.
The source code is fetched from the Unichain Blockscout API and stored in the code/unichain directory.
"""
import json
import os
import os.path

from eth_typing import HexAddress, HexStr

from utils import _cache_base
from utils.paths import open_with_mkdir


def to_hex_address(_str: str) -> HexAddress:
    """
    Convert a string to a hex address
    :param _str: string address
    :return: hex address
    """
    return HexAddress(HexStr(_str))


def store_all_dependencies(_address: str) -> list[str]:
    """
    Store all dependencies of a contract
    :param _address: address of the contract
    :return: paths where the source code is stored
    """
    _address: HexAddress = to_hex_address(_address)
    _file_path = os.path.join(_cache_base, "json", f"{_address}.json")
    _json = get_contract_json(_address)

    try:
        _keys = [_json["file_path"]]
    except KeyError:
        os.remove(_file_path)
        raise KeyError("Server returned invalid JSON")

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


def store_remappings(_address: str) -> list[str]:
    """
    Store the remappings of a contract
    :param _address: address of the contract
    :return: remappings in list format
    """
    _address = to_hex_address(_address)
    _file_path = os.path.join(_cache_base, "json", f"{_address}.json")

    import json
    with open(_file_path, "r") as j:
        _json = json.load(j)
        try:
            _remappings = str.join("\n", _json["compiler_settings"]["remappings"])
            with open_with_mkdir(os.path.join(_cache_base, "remappings.txt"), "w") as f:
                f.write(_remappings)
                return _json["compiler_settings"]["remappings"]
        except KeyError:
            return []


def store_foundry_toml() -> None:
    """
    Store the foundry toml
    """
    _toml_content: str = """[profile.default]
src = "src"
out = "out"
libs = ["lib"]
evm-version = "cancun"
via_ir = true
"""
    try:
        with open_with_mkdir(os.path.join(_cache_base, "foundry.toml"), "x") as f:
            f.write(_toml_content)
    except FileExistsError:
        pass


def store_unichain_contract(_address: str) -> str:
    """
    Get the source unichain of an address.
    :param _address: The address to get the source unichain of.
    :return: path where the target contract code is stored
    """
    _paths = store_all_dependencies(_address)
    store_remappings(_address)
    store_foundry_toml()
    return _paths[0]


def get_contract_json(_address: HexAddress | str) -> dict:
    """
    Get the json object of a contract
    :param _address: address of the contract
    :return: API JSON response
    """
    _address: HexAddress = HexAddress(HexStr(_address))
    _file_path = os.path.join(_cache_base, "json", f"{_address}.json")
    try:
        # force cache, since no need to fetch the same contract source code multiple times
        with open(_file_path, "r") as j:
            _json = json.load(j)
    except (FileNotFoundError, json.JSONDecodeError):
        with open_with_mkdir(_file_path, "w") as j:
            _api_endpoint = "https://unichain-sepolia.blockscout.com/api/v2/smart-contracts/"
            import requests
            _json = requests.get(
                f"{_api_endpoint}{_address}",
                headers={"Content-Type": "application/json", "Cache-Control": "public"},
            ).json()
            json.dump(_json, j)
    return _json
