from slither import slither


def run_cli(_command: str) -> str:
    import subprocess

    return subprocess.run(_command, shell=True, capture_output=True).stdout.decode("utf-8")


def match_solc_version(_solc_version: str, auto_install=False) -> bool:
    if _solc_version in run_cli("solc --version"):
        return True

    if _solc_version in run_cli("solc-select versions"):
        run_cli(f"solc-select use {_solc_version}")
        print(f"Switched to solc {_solc_version}")
        return True
    elif auto_install:
        print(f"Installing solc {_solc_version}")
        run_cli(f"solc-select install {_solc_version}")
        run_cli(f"solc-select use {_solc_version}")
        print(f"Switched to solc {_solc_version}")
        return True
    else:
        print(f"Please install solc {_solc_version}")
        return False


def trial():
    solc_version = "0.8.26"
    if not match_solc_version(solc_version, True):
        return

    run_cli(f"solc-select use {solc_version}")

    a = slither.Slither(
        target="code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol",
        printers_to_run=["callgraph", "cfg", "statespace"],
    )

    return a


if __name__ == "__main__":
    trial()
