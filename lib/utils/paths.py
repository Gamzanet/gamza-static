import json
import os
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


if __name__ == "__main__":
    print(rule_rel_path_by_name("misconfigured-Hook"))
    print(rule_rel_path_by_name("info-variable"))
