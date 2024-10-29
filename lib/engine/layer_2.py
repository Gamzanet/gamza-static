import json

from jmespath import search

from engine.run_semgrep import get_semgrep_output, run_semgrep_one
from layers.Builder import get_variables


def is_valid_hook(_target_path="code/1.sol"):
    # Get the output of the semgrep command
    output: list[dict[str, str]] = run_semgrep_one("misconfigured-Hook", _target_path)

    # group output["data"]["SIG"]
    # group output["data"]["IMPL"]
    permissions = set(search("[*].data.SIG", output))
    impls = search("[*].data.IMPL", output)
    impls = set(map(lambda x: x.split("(")[0], impls))
    res = permissions - impls  # intersect the two groups
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
    with open("out/modifiers.json", "w") as f:
        json.dump(res, f)
    return res


def detect_storage_overwrite_in_multi_pool_initialization(
    _target_path="code/4.sol"
) -> dict:
    _target_functions = {"beforeInitialize", "afterInitialize"}
    _storage_candidates = dict()

    # 1. add candidates from info-variables
    variables: dict[str, list[dict]] = get_variables(_target_path)
    # out = search("@.*[].{NAME:NAME}", variables) # TODO: use JMESPath
    # pprint(out)
    for name, usages in variables.items():
        for usage in usages:
            # mutable storage variables
            # add type to the key for later validation
            if usage["LOCATION"] == "storage" or usage["SCOPE"] == "storage":
                if usage["MUTABLE"] == "mutable":
                    key = f"{usage['SIG']}:{usage['NAME']}"
                    _storage_candidates[key] = usage["TYPE"]

    # TODO: Refactor the following code to a function
    # 2. get info-layer2-assignee
    output: list = get_semgrep_output(
        "info-layer2-assignee",
        _target_path, use_cache=True)
    output = search("[*].data", output)
    for o in output:
        if o["SIG"] in _target_functions:
            key = f"{o['CONTRACT']}:{o['LVALUE']}"
            if key in _storage_candidates.keys():
                _type = _storage_candidates[key]
                # TODO: type_check discussion
                for type_check in ["PoolId", "mapping"]:
                    if type_check in _type:
                        continue
                return {
                    "CONTRACT": o["CONTRACT"],
                    "LVALUE": o["LVALUE"],
                    "TYPE": _type,
                    "SIG": o["SIG"],
                }
    return {}
