import os.path
import subprocess

import etherscan.unichain

_base_dir = os.path.join("code", "unichain")

def store_unichain_contract(_address: str) -> str:
    """
    Get the source unichain of an address.
    :param _address: The address to get the source unichain of.
    :return path where the target contract code is stored
    """
    _paths = etherscan.unichain.store_all_dependencies(_address)
    etherscan.unichain.store_remappings(_address)
    return _paths[0]


def compile_slither(_path: str) -> list[str]:
    """
    Compile the contract using slither.
    :param _path: The path to the contract to compile.
    :return: The output of the compilation.
    """
    os.chdir(_base_dir)
    _res = subprocess.run([
        "slither",
        _path,
        "--solc-remaps",
        "remappings.txt",
        "--solc-solcs-select",
        "0.8.26"
    ], capture_output=True, encoding="utf-8")
    return [_res.stderr, _res.stdout]
