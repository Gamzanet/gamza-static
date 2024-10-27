import os
import sys
from os.path import join as _join


def base_paths(x: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), x))


# to run `python main.py` in root dir, add path of library to sys.path
project_root = base_paths(".")
_path_lib = base_paths("lib")
_path_code = base_paths("code")
sys.path.append(_path_lib)

os.chdir(project_root)
sys.path.append(_join(project_root, "lib"))

import engine.foundry
import engine.slither
from layers.Aggregator import Aggregator
from layers.Loader import Loader

from utils.unichain import store_foundry_toml, store_remappings, store_all_dependencies
from utils import foundry_dir


def test_integration():
    # _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"  # Uniswap v4 PoolManager in unichain
    _address: str = "0x7d61d057dD982b8B0A05a5871C7d40f8b96dd040"  # Entropy First Initialized Hook in unichain

    _paths = store_all_dependencies(_address)
    store_remappings(_address)
    store_foundry_toml()

    _diff = engine.foundry.format_code(foundry_dir)  # "code/unichain" directory
    # print(_diff)

    # linting the target contract recursively lints all dependencies
    _res: tuple[str, str] = engine.slither.lint_code(_paths[0])
    # print(res)

    # code in "code/*" dir can simply be read by Loader
    file_name = "DoubleInitHook"
    code = Loader().read_code(f"{file_name}.sol")
    assert len(code) > 0

    # can also read code from absolute path
    file_path = os.path.join(project_root, "code", "DoubleInitHook.sol")
    code = Loader().read_code(file_path)
    assert len(code) > 0

    aggregator = Aggregator()
    res = aggregator.aggregate(code)
    print(res)
    print(project_root)


if __name__ == "__main__":
    test_integration()
