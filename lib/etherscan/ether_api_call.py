import json
import os

import requests
from eth_typing import HexStr, HexAddress
from jmespath import search


# Need $ETHERSCAN_API_KEY in the environment variables
#

# https://api-sepolia.etherscan.io/api
# ?module = contract
# & action = getsourcecode
# & address = 0x64a736aa55958a41bc1b18590ab7dfcb78444dd1
# & apikey = YourApiKeyToken
def _fetch_contract_json(_network: str, _address: str, use_cache: bool = True) -> dict:
    _file_path = f"code/json/{_address}.json"

    # set default caching to True
    # since no need to fetch the same contract source code multiple times
    if use_cache:
        try:
            with open(_file_path, "r") as j:
                return json.load(j)
        except FileNotFoundError:
            pass

    _address = HexAddress(HexStr(_address))

    if _network == "unichain":
        _res = _fetch_contract_json_unichain(_address)
    elif _network == "sepolia":
        _res = _fetch_contract_json_sepolia(_address)
    else:
        print(_network)
        raise ValueError("Invalid network")

    # store the result in a JSON file
    with open(_file_path, "w") as j:
        json.dump(_res, j)
    return _res


def _fetch_contract_json_unichain(_address: str) -> dict:
    _api_endpoint = "https://unichain-sepolia.blockscout.com/api/v2/smart-contracts/"
    _file_path = f"code/json/{_address}.json"
    _address = HexAddress(HexStr(_address))
    return requests.get(
        f"{_api_endpoint}{_address}",
        headers={"Content-Type": "application/json", },
    ).json()


def _fetch_contract_json_sepolia(_address: str) -> dict:
    # export interface Result {
    #   SourceCode: string
    #   ABI: string
    #   ContractName: string
    #   CompilerVersion: string
    #   OptimizationUsed: string
    #   Runs: string
    #   ConstructorArguments: string
    #   EVMVersion: string
    #   Library: string
    #   LicenseType: string
    #   Proxy: string
    #   Implementation: string
    #   SwarmSource: string
    # }
    _api_endpoint = "https://api-sepolia.etherscan.io/api"
    _file_path = f"code/json/{_address}.json"
    _address = HexAddress(HexStr(_address))

    r = requests.get(
        _api_endpoint,
        headers={"Content-Type": "application/json"},
        params={
            "module": "contract",
            "action": "getsourcecode",
            "address": _address.strip(),
            "apikey": os.getenv("ETHERSCAN_API_KEY")
        }).json()
    _res = r.get("result")[0].get("SourceCode")[1:-1]  # remove wrapping brackets {}
    return json.loads(_res)













# input: address
# output: solidity source code
def get_source_from_explorer(_network: str, _address: str, use_cache: bool = False) -> str | None:
    if use_cache:
        try:
            with open(f"code/{_network}_{_address}.sol", "r") as sol:
                return sol.read()
        except FileNotFoundError:
            pass

    _json: dict = _fetch_contract_json(_network, _address)
    print(type(_json))
    print(_json.keys())
    if _network == "unichain":
        try:
            _src = _json['source_code']
        except KeyError:
            return None
    elif _network == "sepolia":
        key: str = search("sources.keys(@)[0]", _json)
        _src = _json['sources'][key]['content']
    else:
        raise ValueError("Invalid network")
    
    with open(f"code/{_network}_{_address}.sol", "w") as f:
        f.write(_src)
    return _src


if __name__ == "__main__":
    address = "0xe8e23e97fa135823143d6b9cba9c699040d51f70"  # Uniswap v4 PoolManager in sepolia
    src = get_source_from_explorer("sepolia", address)
    print(len(src))

    address = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"  # Uniswap v4 PoolManager in unichain
    src = get_source_from_explorer("unichain", address, )
    print(len(src))
