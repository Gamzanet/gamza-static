import os
import re

from etherscan.unichain import store_all_dependencies, store_remappings, foundry_dir, store_foundry_toml
from utils.paths import run_cli_must_succeed, run_cli_can_failed


def format_code(_path: str) -> str:
    diff = run_cli_can_failed(f"forge fmt {_path} --check")[0]
    if diff:
        run_cli_must_succeed(f"forge fmt {_path}")
    return diff


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


def lint_code(_rel_path: str) -> tuple[str, str]:
    """
    Compile the contract using slither.
    :param _rel_path: The relative path to the contract to compile.
    :return: The output of the compilation.
    """
    _origin_dir = os.getcwd()
    os.chdir(foundry_dir)
    set_solc_version_by_sol(_rel_path)
    _res = run_cli_can_failed(f"slither {_rel_path}")
    os.chdir(_origin_dir)
    return _res


def set_solc_version_by_sol(_path: str) -> str:
    """
    Set the solc version from the solidity file.
    :param _path: The path to the solidity file.
    :return: The version of the solidity file.
    """
    with open(_path, "r") as f:
        _content = f.read()
    return set_solc_version_by_content(_content)


def set_solc_version_by_content(_content: str) -> str:
    _version = re.search(r"pragma\s+solidity\s+(?:\W+)?([\d.]+);", _content).group(1)
    set_solc_version(_version)
    return _version


def set_solc_version(_version: str) -> None:
    is_installed = re.search(_version, run_cli_must_succeed(
        "solc-select versions",
        capture_output=True
    ))
    if not is_installed:
        run_cli_must_succeed(f"solc-select install {_version}")
    run_cli_must_succeed(f"solc-select use {_version}")
