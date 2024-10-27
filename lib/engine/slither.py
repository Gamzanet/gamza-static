import os
import re

from extractor.getter import get_solc_version
from utils import foundry_dir
from utils.paths import run_cli_can_failed, run_cli_must_succeed


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
    _version = get_solc_version(_content)
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
