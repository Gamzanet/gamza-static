import hashlib
import json
import os.path
import re
import subprocess

import yaml
from jmespath import search

# TODO: 일일이 경로 지정하지 않아도, 디렉토리 탐색해서 파일명 맞으면 알아서 실행되도록 수정. 파일 트리 만들고 사용해도 됨
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


def get_semgrep_output(_rule_name: str, _target_path: str = "source", caching: bool = False) -> list:
    # try read json output
    _json_file_name = f"{_rule_name}_{_target_path}.json"
    _json_file_name = hashlib.sha256(_json_file_name.encode()).hexdigest()
    if caching:
        try:
            with open(f"out/{_json_file_name}", "r") as f:
                return json.load(f, strict=True)['data']
        except FileNotFoundError:
            pass
    res = run_semgrep(_rule_name, _target_path)
    # print("_res:", res)
    res = re.findall(r"([\w+\/]+\w+.sol:\d+:\d+):([\S]+):([ \S]+):([\w(),.$ |\n]*)(?:^\w+)", res, flags=re.MULTILINE)
    _msg_schema = parse_semgrep_rule_message_by_rule_name(_rule_name)

    _output = []
    for r in res:
        # r = list(map(str.strip, r))
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
    # _value = map(str.strip, _tuple[3].split("|"))
    # _value = re.findall(r"([\S\s]+?)\s+\|", _tuple[3], flags=re.MULTILINE)
    print("tuple[0]:", _tuple[0])
    print("tuple[1]:", _tuple[1])
    print("tuple[2]:", _tuple[2])
    print("tuple[3]:", _tuple[3])

    _value = re.split(r"\|\s+", _tuple[3], flags=re.MULTILINE)
    _value = map(str.strip, _value)
    _data = dict(zip(_key, _value))
    # if value == ${KEY}, then replace with the value to None
    for k, v in _data.items():
        if v == f"${k}" or v == "":
            _data[k] = None
    return {
        "source": _tuple[0],
        "rule": _tuple[1],
        "log": _tuple[2],
        "data": _data
    }


if __name__ == "__main__":
    output = get_semgrep_output("info-function",
                                "source/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol",
                                caching=False)  # get the output of the semgrep analysis
    print(output)
