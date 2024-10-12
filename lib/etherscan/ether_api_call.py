import json
import os

import requests
from eth_typing import HexStr, HexAddress
from jmespath import search


# https://api-sepolia.etherscan.io/api
# ?module = contract
# & action = getsourcecode
# & address = 0x64a736aa55958a41bc1b18590ab7dfcb78444dd1
# & apikey = YourApiKeyToken
def _fetch_contract_json(_address: str, use_cache: bool = True) -> dict:
    _file_path = f"code/json/{_address}.json"

    # set default caching to True
    # since no need to fetch the same contract source code multiple times
    # TODO: currently sepolia only. supports different networks too
    if use_cache:
        try:
            with open(_file_path, "r") as j:
                return json.load(j)
        except FileNotFoundError:
            pass

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
    _address = HexAddress(HexStr(_address))
    r = requests.get(
        "https://api-sepolia.etherscan.io/api",
        headers={"Content-Type": "application/json"},
        params={
            "module": "contract",
            "action": "getsourcecode",
            "address": _address.strip(),
            "apikey": os.getenv("ETHERSCAN_API_KEY")
        }).json()

    # currently only interested in the source code
    res = r.get("result")[0].get("SourceCode")[1:-1]  # remove wrapping brackets {}
    res = json.loads(res)

    # store the result in a JSON file
    with open(_file_path, "w") as j:
        json.dump(res, j)
    return res


# input: address
# output: solidity source code
def get_source_from_etherscan(_address: str, use_cache: bool = False) -> str:
    if use_cache:
        try:
            with open(f"code/{_address}.sol", "r") as sol:
                return sol.read()
        except FileNotFoundError:
            pass

    _json: dict = _fetch_contract_json(_address)
    print(type(_json))
    key: str = search("sources.keys(@)[0]", _json)
    _src = _json['sources'][key]['content']
    with open(f"code/{_address}.sol", "w") as f:
        f.write(_src)
    return _src


if __name__ == "__main__":
    address = "0xe8e23e97fa135823143d6b9cba9c699040d51f70"  # Uniswap v4 PoolManager
    src = get_source_from_etherscan(address)
    print(src)
