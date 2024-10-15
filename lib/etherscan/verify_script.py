import os
import subprocess

import dotenv
import requests

dotenv.load_dotenv()
_anvil_local_network: str = "http://localhost:8545"


def run_forge_script(
    _foundry_abs_path: str,
    _script_rel_path: str,
    _contract_name: str,
    _network: str = _anvil_local_network,
    _private_key: str = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    _broadcast: bool = False,
    _verifier: str = "blockscout"
):
    _script_abs_path = os.path.join(_foundry_abs_path, _script_rel_path)
    # script path validation
    with open(_script_abs_path, "r") as f:
        assert len(f.read()) > 0

    # forge script
    if _network == _anvil_local_network:
        anvil_must_running()

    # run cli forge script
    # forge script script/Deploy.sol -f local
    _args = [
        "cd", _foundry_abs_path, "&&",
        "forge", "script", f"{_script_rel_path}",
        "-f", _network,
        "--private-key", _private_key,
        "--slow",
    ]
    if _broadcast:
        _args.append("--broadcast")
        if _verifier == "blockscout":
            if _network == _anvil_local_network:
                raise SystemExit("Error: cannot use verifier with local network")
            _args.append("--verify")
            _args.append(f"--verifier={_verifier}")
            _unichain_verifier = "https://unichain-sepolia.blockscout.com/api/"  # --verifier-url
            _args.append(f"--verifier-url={_unichain_verifier}")

    _out = subprocess.run(_args, capture_output=True, text=True)
    print(_out)
    print(_out.stdout)
    if _out.stderr:
        print(_out.stderr)

    pass


def anvil_must_running():
    try:
        response = requests.post(
            "http://localhost:8545",
            json={"jsonrpc": "2.0", "method": "web3_clientVersion", "params": [], "id": 1},
            headers={"Content-Type": "application/json"}
        )
        if "anvil" in response.json()["result"]:
            print("Anvil local network is running")
        print(f"use network: {response.json()["result"]}")

    except requests.exceptions.RequestException:
        raise SystemExit("Error: manually run anvil local network first")


def get_project_root_dir() -> str:
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    return os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))


if __name__ == "__main__":
    _foundry_abs_path = os.path.join(get_project_root_dir(), "foundry/cookie")
    _script_rel_path = "script/Deploy.sol"
    _contract_name = "Deploy"
    # use anvil local network as default
    run_forge_script(
        _foundry_abs_path,
        _script_rel_path,
        _contract_name,
        _network="https://unichain-sepolia.g.alchemy.com/v2/S4JLchhpwNEjAg296euR_8-GRTlhqwmJ",
        _broadcast=True,
    )
