import os.path
from pprint import pprint

from engine import layer_0
from etherscan.unichain import store_foundry_toml, store_remappings, store_all_dependencies, unichain_dir
from parser.layer_2 import get_variables
from parser.run_semgrep import get_semgrep_output


def test_integration():
    # _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"  # Uniswap v4 PoolManager in unichain
    _address: str = "0x7d61d057dD982b8B0A05a5871C7d40f8b96dd040"  # Entropy First Initialized Hook in unichain

    _paths = store_all_dependencies(_address)
    store_remappings(_address)
    store_foundry_toml()

    layer_0.format_code(unichain_dir)  # "code/unichain" directory

    # linting the target contract recursively lints all dependencies
    res: list[str] = layer_0.compile_slither(_paths[0])
    print(res)

    # to run semgrep rules,
    # path needs to start with "code"
    _target_path = os.path.join(unichain_dir, _paths[0])

    _output_l: list = get_semgrep_output(
        "misconfigured-Hook",
        _target_path,
        False
    )
    pprint(_output_l)

    _output_l: list = get_semgrep_output(
        "info-variable",
        _target_path,
        False
    )
    pprint(_output_l)

    _output_d: dict = get_variables(_target_path)
    pprint(_output_d)
