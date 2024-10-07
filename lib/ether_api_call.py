import json
import os

import requests
from dotenv import load_dotenv
from eth_typing import HexStr, HexAddress
from jmespath import search

load_dotenv()


# https://api-sepolia.etherscan.io/api
# ?module = contract
# & action = getsourcecode
# & address = 0x64a736aa55958a41bc1b18590ab7dfcb78444dd1
# & apikey = YourApiKeyToken
def get_source_json(_address: str) -> any:
    _address = HexAddress(HexStr(_address))
    # TODO: currently sepolia only. supports ethereum mainnet too
    r = requests.get("https://api-sepolia.etherscan.io/api", params={
        "module": "contract",
        "action": "getsourcecode",
        "address": _address.strip(),
        "apikey": os.getenv("ETHERSCAN_API_KEY")
    })

    # store the result in a JSON file
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
    with open(f"source/json/{_address}.json", "w") as f:
        res = search("result[0].SourceCode", r.json())
        res = res.replace("{{", "{").replace("}}", "}")  # TODO: parse top-level bracket
        f.write(res)
        return res


if __name__ == "__main__":
    address = "0xe8e23e97fa135823143d6b9cba9c699040d51f70"  # Uniswap v4 PoolManager
    src_json = get_source_json(address)

    with open(f"source/json/{address}.json", "r") as j:
        pm = json.load(j)
        key = search("sources.keys(@)[0]", pm)  # lib/v4-core/src/PoolManager.sol
        src = pm['sources'][key]['content']
        with open(f"source/{address}.sol", "w") as f:
            print(src)
            f.write(src)
