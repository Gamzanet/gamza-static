import os.path
import subprocess

import etherscan.unichain


def run_cli(_command: str, capture_output=False) -> str | None:
    return subprocess.run(_command, shell=True, capture_output=capture_output, text=True).stdout


def format_code(_path: str):
    res: str = run_cli(f"forge fmt {_path} --check", True)
    print(res)
    if len(res) > 0:
        print("Code is not formatted properly")
        run_cli("forge fmt code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol", False)
    else:
        print("Code is formatted properly")


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
    _base_dir = os.path.join("code", "unichain")
    os.chdir(_base_dir)
    # TODO: parse solc version from the contract
    _res = subprocess.run([
        "slither",
        os.path.join(_base_dir, _path),
        "--solc-remaps",
        os.path.join(_base_dir, "remappings.txt"),
        "--solc-solcs-select",
        "0.8.26"
    ], capture_output=True, encoding="utf-8")
    return [_res.stderr, _res.stdout]


if __name__ == "__main__":
    _address: str = "0x38EB8B22Df3Ae7fb21e92881151B365Df14ba967"
    format_code(_address)
    compile_slither(_address)
