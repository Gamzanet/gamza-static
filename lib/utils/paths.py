import json
import os
import subprocess
from typing import TextIO

from utils import project_root_abs


def open_with_mkdir(file_path: str, mode: str) -> TextIO:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return open(file_path, mode)


def rule_rel_path_by_name(rule_name: str) -> str:
    _mapper = "mapping_ruleName_path.json"
    with open(os.path.join(project_root_abs, "rules", _mapper), "r") as f:
        rules = json.load(f)
        class_name = "info" if "info-" in rule_name else rules["class"][rule_name]
        return str(os.path.join(rules["root"], class_name, f"{rule_name}.yaml"))


def run_cli_must_succeed(_command: str, capture_output=False) -> str:
    out = subprocess.run(_command, shell=True, capture_output=capture_output, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"Command failed: {_command} with {out.returncode}")
    return out.stdout


def run_cli_can_failed(_command: str) -> tuple[str, str]:
    out = subprocess.run(_command, shell=True, capture_output=True, text=True)
    return out.stdout, out.stderr


if __name__ == "__main__":
    print(rule_rel_path_by_name("misconfigured-Hook"))
    print(rule_rel_path_by_name("info-variable"))
