import json
from pprint import pprint

from jmespath import search

from parser.run_semgrep import get_semgrep_output


def is_valid_hook(_target_path="code/1.sol"):
    # Get the output of the semgrep command
    output: list = get_semgrep_output("misconfigured-Hook", _target_path)
    pprint(output)

    # group output["data"]["SIG"]
    # group output["data"]["IMPL"]
    # intersect the two groups
    sig = set(search("[*].data.SIG", output))
    # print(sig)
    impl = set(search("[*].data.IMPL", output))
    # print(impl)
    res = sig - impl
    if res:
        print(f"{_target_path}:", ', '.join(res), "is not implemented")
        return False
    return True


# currently source code should include single contract
def get_modifiers(_target_path="code/3.sol"):
    # [*].data.CONTRACT
    # [*].data.SIG
    # [*].data.VIS
    # [*].data.PAY
    # [*].data.PURITY
    # [*].data.MOD
    # [*].data.RETURN
    output: list = get_semgrep_output("info-function", _target_path)

    res = {}
    # TODO: JMESPath 내장 기능을 활용하여 구현해보기
    for e in list(search("[*].data[]", output)):
        if e["MOD"] is not None:
            import re
            mods = re.split(r"\s", e["MOD"])
            for mod in mods:
                mod = mod.strip()
                if mod not in res.keys():
                    res[mod] = []

                inline = ''.join(re.split(r"(?<=[,()])\s+|\s+(?=\))", e['SIG'], flags=re.MULTILINE))
                contract_sig = f"{e['CONTRACT']}:{inline}"
                res[mod].append(contract_sig)
    json.dump(res, open("out/modifiers.json", "w"))
    return res


def get_variables(_target_path="code/1.sol"):
    output: list = get_semgrep_output("info-variable", _target_path)
    return output
