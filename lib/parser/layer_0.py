import subprocess


def run_cli(_command: str, capture_output=False) -> str | None:
    return subprocess.run(_command, shell=True, capture_output=capture_output, text=True).stdout


def format_code():
    res: str = run_cli("forge fmt code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol --check", True)
    print(res)
    if len(res) > 0:
        print("Code is not formatted properly")
        run_cli("forge fmt code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol", False)
    else:
        print("Code is formatted properly")


def lint_code():
    res: str = run_cli("solhint code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol --disc")
    print(res)
    if len(res) > 0:
        print("Code is not linted properly")
    else:
        print("Code is linted properly")


if __name__ == "__main__":
    format_code()
    lint_code()
