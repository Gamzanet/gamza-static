import re
import subprocess

import yaml
from jmespath import search


# read semgrep rule to run
# save variable context
def read_semgrep_rule_by_file_name(_file_name: str):
    res = None
    with open(_file_name, "r") as f:
        file = f.read()
        res = yaml.safe_load(file)
        res = search("rules[0].message", res)
        # print(res)
    return res


def parse_semgrep_rule_message_by_file_name(_file_name: str):
    _msg = read_semgrep_rule_by_file_name(_file_name)
    # print(_msg)
    res = re.findall(r"\$(\w+)", _msg, flags=re.MULTILINE)
    # print(res)
    return res


# TODO: run semgrep rules
# CLI: npm run case2
def run_semgrep():
    subprocess.run(["npm", "run", "case2"])
    pass


# TODO: get the output of the semgrep analysis
def get_semgrep_output():
    pass


# TODO: read result of the analysis
def read_semgrep_output():
    pass


# TODO: run semgrep JSON output to the use
def run_semgrep_json():
    pass


def is_no_op():
    return False


if __name__ == "__main__":
    msg = parse_semgrep_rule_message_by_file_name("rules/misconfigured-Hook.yaml")  # read semgrep rule
    print(msg)
    run_semgrep()  # semgrep result stored in a JSON file
    get_semgrep_output()  # get the output of the semgrep analysis
    read_semgrep_output()  # read result of the analysis
    run_semgrep_json()  # run semgrep JSON output to the use
