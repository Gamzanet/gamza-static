import re
from threading import Condition

from jmespath import search

from engine.lexer import Tokenizer, ConditionStack
from engine.run_semgrep import get_semgrep_output


def get_contract_name(_code: str) -> str | None:
    _s = re.search(r"contract\s+(\w+)[\s\S]+?{", _code)
    return _s.group(1) if _s else None


def get_inheritance(target_abs_path: str) -> list[str]:
    if not target_abs_path:
        raise ValueError
    info_inheritance: list[dict] = get_semgrep_output("info-inheritance", target_abs_path)
    return search("[*].data.INHERIT", info_inheritance)


def get_library(target_abs_path: str) -> list[str]:
    if not target_abs_path:
        raise ValueError
    info_library: list[dict] = get_semgrep_output("info-library", target_abs_path)
    return search("[*].data.LIBRARY", info_library)


def get_license(_code: str) -> str | None:
    _s = re.search(r"//\s*SPDX-License-Identifier:\s*(.*)", _code)
    return _s.group(1) if _s else None


def get_function_body(_target_path: str) -> list[dict]:
    return get_semgrep_output("info-function-body", _target_path)


def get_imports(_code):
    _has_imports = re.findall(r"import\s+([\s\S]+?);", _code)
    return _has_imports if _has_imports else []


def get_conditions(code: str) -> list[Condition]:
    _tokenized = Tokenizer.tokenize(code)

    stack = ConditionStack()
    for line in _tokenized:
        if line != "":
            stack.push(line.strip())
    return stack.conditions


def get_solc_version(_content: str) -> str | None:
    _s = re.search(r"pragma\s+solidity\s+(?:\W+)?([\d.]+);", _content)
    return _s.group(1) if _s else None
