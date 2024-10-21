import os
import sys

# to run `python main.py` in root dir, add path of library to sys.path
_path_lib = os.path.abspath(os.path.join(os.path.dirname(__file__), "lib"))
sys.path.append(_path_lib)

from utils.paths import rule_rel_path_by_name
from engine import layer_0
from etherscan.unichain import store_foundry_toml, store_remappings, store_all_dependencies, foundry_dir
from parser.layer_2 import get_variables
from parser.run_semgrep import get_semgrep_output


def test_integration():
    # _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"  # Uniswap v4 PoolManager in unichain
    _address: str = "0x7d61d057dD982b8B0A05a5871C7d40f8b96dd040"  # Entropy First Initialized Hook in unichain

    _paths = store_all_dependencies(_address)
    store_remappings(_address)
    store_foundry_toml()

    _diff = layer_0.format_code(foundry_dir)  # "code/unichain" directory
    # print(_diff)

    # linting the target contract recursively lints all dependencies
    _res: list[str] = layer_0.lint_code(_paths[0])
    # print(res)

    # to run semgrep rules,
    # path needs to start with "code"
    _target_path = os.path.join(foundry_dir, _paths[0])

    _output_l1: list = get_semgrep_output(
        rule_rel_path_by_name("misconfigured-Hook"),
        _target_path,
        False
    )
    # pprint(_output_l)

    _output_l2: list = get_semgrep_output(
        rule_rel_path_by_name("info-variable"),
        _target_path,
        False
    )
    # pprint(_output_l)

    _output_d: dict = get_variables(_target_path)
    # pprint(_output_d)

    assert len(_output_l1) > 0
    assert len(_output_l2) > 0
    assert _output_d != {}


if __name__ == "__main__":
    test_integration()
