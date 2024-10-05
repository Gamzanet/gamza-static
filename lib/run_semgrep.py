import hashlib
import json
import os.path
import re
import subprocess
from pprint import pprint

import yaml
from jmespath import search

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(path)


# TODO: encapsulate routines in a class
# read semgrep rule to run
# save variable context
def read_semgrep_rule_by_rule_name(_rule_name: str):
    res = None
    with open(f"rules/{_rule_name}.yaml", "r") as f:
        file = f.read()
        res = yaml.safe_load(file)
        res = search("rules[0].message", res)
        # print(res)
    return res


def parse_semgrep_rule_message_by_rule_name(_rule_name: str):
    _msg = read_semgrep_rule_by_rule_name(_rule_name)
    # print(_msg)
    res = re.findall(r"\$(\w+)", _msg, flags=re.MULTILINE)
    # print(res)
    return res


# CLI: npm run case2
def run_semgrep(_rule_name: str, _target_path: str = "source") -> str:
    # semgrep scan -f rules/misconfigured-Hook.yaml source --emacs
    print(_rule_name, _target_path)
    res = subprocess.run(["semgrep", "scan", "-f", f"rules/{_rule_name}.yaml", _target_path, "--emacs"],
                         capture_output=True)
    res = res.stdout.decode("utf-8")
    print(res)
    return res


def get_semgrep_output(_rule_name: str, _target_path: str = "source") -> list:
    # try read json output
    _json_file_name = f"{_rule_name}_{_target_path}.json"
    _json_file_name = hashlib.sha256(_json_file_name.encode()).hexdigest()
    try:
        with open(f"out/{_json_file_name}", "r") as f:
            return json.load(f, strict=True)['data']
    except FileNotFoundError:
        res = run_semgrep(_rule_name, _target_path)
        res = re.findall(r"(\S+:\S+):(\S+):([ \S]+):([ \S]+)", res, flags=re.MULTILINE)
        # pprint(res)
        _msg_schema = parse_semgrep_rule_message_by_rule_name(_rule_name)

        _output = []
        for r in res:
            _output.append(emacs_tuple_to_dict(r, _msg_schema))
        with open(f"out/{_json_file_name}", "w") as f:
            json.dump({"data": _output}, f)
            return _output


def emacs_tuple_to_dict(_tuple: tuple, _msg_schema: list):
    # source:   ('source/1.sol:6:1',
    # rule:     'warning(misconfigured-Hook-2)',
    # log:      'contract ExampleHook is BaseHook {',
    # message:  'ExampleHook | $SIG | $IMPL')
    _key = _msg_schema
    _value = map(str.strip, _tuple[3].split("|"))
    _data = dict(zip(_key, _value))
    # if value == ${KEY}, then replace with the value to None
    for k, v in _data.items():
        if v == f"${k}":
            _data[k] = None
    return {
        "source": _tuple[0],
        "rule": _tuple[1],
        "log": _tuple[2],
        "data": _data
    }


if __name__ == "__main__":
    output = get_semgrep_output("misconfigured-Hook", "source")  # get the output of the semgrep analysis
    pprint(output)
