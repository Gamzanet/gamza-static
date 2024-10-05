import json
import re
import subprocess
from pprint import pprint

import yaml
from jmespath import search


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


# TODO: should run case based on user input
# CLI: npm run case2
def run_semgrep(_rule_name: str, _target_dir: str = "source") -> str:
    # semgrep scan -f rules/misconfigured-Hook.yaml source --emacs
    print(_rule_name, _target_dir)
    res = subprocess.run(["semgrep", "scan", "-f", f"rules/{_rule_name}.yaml", _target_dir, "--emacs"],
                         capture_output=True)
    res = res.stdout.decode("utf-8")
    print(res)
    return res


def get_semgrep_output(_rule_name: str, _target_dir: str = "source") -> list:
    # try read json output
    try:
        with open(f"out/{_rule_name}.json", "r") as f:
            return json.load(f, strict=True)['data']
    except FileNotFoundError:
        res = run_semgrep(_rule_name, _target_dir)
        res = re.findall(r"(\S+:\S+):(\S+):([ \S]+):([ \S]+)", res, flags=re.MULTILINE)
        # pprint(res)
        _msg_schema = parse_semgrep_rule_message_by_rule_name(_rule_name)

        _output = []
        for r in res:
            _output.append(emacs_tuple_to_dict(r, _msg_schema))
        with open(f"out/{_rule_name}.json", "w") as f:
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


# TODO: read result of the analysis
def read_semgrep_output():
    pass


# TODO: run semgrep JSON output to the use
def run_semgrep_json():
    pass


def is_no_op():
    return False


if __name__ == "__main__":
    output = get_semgrep_output("misconfigured-Hook", "source")  # get the output of the semgrep analysis
    pprint(output)
    read_semgrep_output()  # read result of the analysis
    run_semgrep_json()  # run semgrep JSON output to the use
