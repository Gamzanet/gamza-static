import json
import re
import subprocess

import yaml
from jmespath import search


# save variable context
# rule should be in the `rules` directory
def read_message_schema_by_rule_name(_rule_name: str):
    try:
        with open(f"rules/{_rule_name}.yaml", "r") as f:
            file = f.read()
            res = yaml.safe_load(file)
            res = search("rules[0].message", res)
            print("res:", res)
            return res
    except FileNotFoundError:
        raise FileNotFoundError(f"rules/{_rule_name}.yaml not found")


# input: $CONTRACT | $SIG | $VIS | $PAY | $PURITY | $MOD | $OVER | $RETURN
# output: ['CONTRACT', 'SIG', 'VIS', 'PAY', 'PURITY', 'MOD', 'OVER', 'RETURN']
def parse_message_schema(_msg_schema: str):
    res = re.findall(r"\$(\w+)", _msg_schema, flags=re.MULTILINE)
    return res


# CLI: npm run case2
def run_semgrep(_rule_name: str, _target_path: str = "code") -> str:
    # semgrep scan -f rules/misconfigured-Hook.yaml code --emacs
    print(_rule_name, _target_path)
    res = subprocess.run(["semgrep", "scan", "-f", f"rules/{_rule_name}.yaml", _target_path, "--emacs"],
                         capture_output=True)
    res = res.stdout.decode("utf-8")
    # print(res)
    return res


def get_semgrep_output(_rule_name: str, _target_path: str = "code", use_cache: bool = False) -> list:
    # try read json output
    _json_file_name = f"{_rule_name}_{_target_path.replace("/", "-")}.json"

    if use_cache:
        try:
            with open(f"out/{_json_file_name}", "r") as f:
                return json.load(f, strict=True)['data']
        except FileNotFoundError:
            pass

    _output = []
    res = run_semgrep(_rule_name, _target_path)
    # print("_res:", res)
    res = re.findall(r"([\w+\/]+\w+.sol:\d+:\d+):([\S]+):([ \S]+):([\w(),.$ |\n]*)(?:^\w+)", res, flags=re.MULTILINE)

    _msg_raw_schema = read_message_schema_by_rule_name(_rule_name)
    _msg_schema = parse_message_schema(_msg_raw_schema)

    for r in res:
        # r = list(map(str.strip, r))
        _output.append(emacs_tuple_to_dict(r, _msg_schema))

    with open(f"out/{_json_file_name}", "w") as f:
        json.dump({"data": _output}, f)

    return _output


def emacs_tuple_to_dict(_tuple: tuple, _msg_schema: list):
    # code:   ('code/1.sol:6:1',
    # rule:     'warning(misconfigured-Hook-2)',
    # log:      'contract ExampleHook is BaseHook {',
    # message:  'ExampleHook | $SIG | $IMPL')
    _key = _msg_schema
    # _value = map(str.strip, _tuple[3].split("|"))
    # _value = re.findall(r"([\S\s]+?)\s+\|", _tuple[3], flags=re.MULTILINE)
    # print("tuple[0]:", _tuple[0])
    # print("tuple[1]:", _tuple[1])
    # print("tuple[2]:", _tuple[2])
    # print("tuple[3]:", _tuple[3])

    _value = re.split(r"\|\s+", _tuple[3], flags=re.MULTILINE)
    _value = map(str.strip, _value)
    _data = dict(zip(_key, _value))
    # if value == ${KEY}, then replace with the value to None
    for k, v in _data.items():
        if v == f"${k}" or v == "":
            _data[k] = None
    return {
        "code": _tuple[0],
        "rule": _tuple[1],
        "log": _tuple[2],
        "data": _data
    }


if __name__ == "__main__":
    output = get_semgrep_output("info-function",
                                "code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol",
                                use_cache=False)  # get the output of the semgrep analysis
    # print(output)
