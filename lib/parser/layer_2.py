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


def get_variables(_target_path="code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol"):
    output: list = get_semgrep_output("info-variable", _target_path)
    pre_process_atomic_var(output)
    pass


def pre_process_atomic_var(_vars: list[dict]) -> list:
    _res = []
    for _var in _vars:
        _var: dict = _var.get("data")
        # {'CONTRACT': 'PoolManager', 'SIG': 'modifyLiquidity', 'ARGS': None, 'RETURNS': None, 'IMPL': None,
        #  'TYPE': 'BalanceDelta', 'LOCATION': None, 'VISIBLE': None, 'MUTABLE': None, 'NAME': 'principalDelta'}

        _var["ARGS"] = list(map(str.strip, _var.get("ARGS").split(","))) if _var.get("ARGS") else None
        # print(_var.get("ARGS")) # ['PoolKey memory key', 'uint24 newDynamicLPFee']
        _var["RETURNS"] = list(map(str.strip, _var.get("RETURNS").split(","))) if _var.get("RETURNS") else None
        # print(_var.get("RETURNS")) # ['Pool.State storage']


# return True if the variable is named variable
def is_named_variable(_name: str) -> bool:
    return False


def classify_variables(_var: dict) -> dict:
    # 'ARGS': PoolKey memory key, BalanceDelta delta, address target
    # 'CONTRACT': 'ExampleHook',
    # 'IMPL': None,
    # 'LOCATION': None,
    # 'MUTABLE': None,
    # 'NAME': 'name',
    # 'RETURNS': None,
    # 'SIG': None,
    # 'TYPE': 'string',
    # 'VISIBLE': 'public'
    # to
    # { $NAME: [
    #   {
    #       "SIG": $CONTRACT:$SIG
    #       "SCOPE": "function:$LOCATION" | "storage:$VISIBLE" | "storage:inherited",
    #       "TYPE": $TYPE,
    #       "MUTABLE": "mutable" | "immutable" | "constant" | "transient"
    #   },
    # ]}
    if _var["SIG"] or _var["ARGS"] or _var["RETURNS"] or _var["IMPL"]:
        if _var["LOCATION"]:
            return False
    if _var["MUTABLE"] or _var["VISIBLE"]:
        return False
    if _var["TYPE"] or _var["CONTRACT"] or _var["NAME"]:
        return False
    return False


if __name__ == '__main__':
    get_variables()
