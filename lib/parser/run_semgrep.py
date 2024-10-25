import json
import os
import re
import subprocess

import yaml
from jmespath import search

from utils.paths import open_with_mkdir, run_cli_must_succeed


# save variable context
# rule should be in the `rules` directory
def read_message_schema_by_rule_name(_rule_path: str):
    print(os.getcwd())
    try:
        with open(f"rules/{_rule_path}", "r") as f:
            file = f.read()
    except FileNotFoundError:
        with open(_rule_path, "r") as f:
            file = f.read()
    res = yaml.safe_load(file)
    res = search("rules[0].message", res)
    # print("read_message_schema_by_rule_name:", res)
    return res

# input: $CONTRACT |&| $SIG |&| $LVALUE |&| $RVALUE |;|
# output: ['CONTRACT', 'SIG', 'LVALUE', 'RVALUE']
def parse_message_schema(_msg_schema: str) -> list[str]:
    return re.findall(r"\$(\w+)", _msg_schema, flags=re.MULTILINE)


# CLI: npm run case2
def run_semgrep_one(_rule_path: str, _target_path: str = "code") -> list[dict]:
    _msg_raw_schema = read_message_schema_by_rule_name(_rule_path)
    _msg_schema = parse_message_schema(_msg_raw_schema)

    arg = f"semgrep scan -f rules/{_rule_path} {_target_path} --emacs"
    res = run_cli_must_succeed(arg, capture_output=True)
    parsed = parse_emacs_output(res)

    _output = []
    for r in parsed:
        _output.append(emacs_tuple_to_dict_with_schema(r, _msg_schema))
    return _output


def parse_emacs_output(_emacs: str):
    """
    Parse the output of the semgrep command.
    :param _emacs: The output of the semgrep command.
    :return: A list of tuples in sequence: (code, severity, rule, log, message)
    """
    return re.findall(
        r"(\S+.sol:\d+:\d+):(\S+)\((\S+)\):\s*([\S ]*):([\s\S]+?)\|;\|",
        _emacs, flags=re.MULTILINE)


def run_semgrep_raw_msg(_target_path: str = "code") -> list[tuple]:
    # semgrep scan -f rules/misconfigured-Hook.yaml code --emacs
    res = subprocess.run(
        ["semgrep", "scan", "-f", "rules/raw", _target_path, "--emacs"],
        capture_output=True
    ).stdout.decode("utf-8")

    parsed = re.findall(
        r"(code[\w+/]+\w+.sol:\d+:\d+):(\S+):([ \S]+):([\w(),.$=> |\n]*)(?=code)\b",
        res, flags=re.MULTILINE)

    return parsed


def get_semgrep_output(_rule_name: str, _target_path: str = "code", use_cache: bool = False) -> list:
    # try read json output
    _json_file_name = f"{_rule_name}_{_target_path.replace("/", "-")}.json"

    if use_cache:
        try:
            with open(f"out/{_json_file_name}", "r") as f:
                return json.load(f, strict=True)['data']
        except FileNotFoundError:
            pass

    _output: list[dict] = run_semgrep_one(_rule_name, _target_path)

    json.dump(
        {"data": _output},
        open_with_mkdir(f"out/{_json_file_name}", "w")
    )

    return _output


def emacs_tuple_to_dict_with_schema(_tuple: tuple, _msg_schema: list) -> dict:
    # code:   ('code/1.sol:6:1',
    # severity: 'warning',
    # rule:     'misconfigured-Hook-2',
    # log:      'contract ExampleHook is BaseHook {',
    # message:  'ExampleHook | $SIG | $IMPL')
    _key = _msg_schema

    _value = re.split(r"\s*\|&\|\s*", _tuple[4], flags=re.MULTILINE)
    _value = map(str.strip, _value)
    _data = dict(zip(_key, _value))
    # if value == ${KEY}, then replace with the value to None
    for k, v in _data.items():
        if v == f"${k}" or v == "":
            _data[k] = None
    return {
        "code": _tuple[0],
        "severity": _tuple[1],
        "rule": _tuple[2],
        "log": _tuple[3],
        "data": _data
    }


def emacs_tuple_to_dict(_tuple: tuple):
    _value = re.split(r"\|\s+", _tuple[3], flags=re.MULTILINE)
    _value = map(str.strip, _value)
    return {
        "code": _tuple[0],
        "rule": _tuple[1],
        "log": _tuple[2],
        "data": _value
    }
