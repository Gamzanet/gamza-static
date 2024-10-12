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
    output: list[dict] = get_semgrep_output("info-variable", _target_path)
    # OUTPUT
    # [{ 'code': 'code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol:381:5',
    #    'data': {'ARGS': 'PoolKey memory key, BalanceDelta delta, address target',
    #              'CONTRACT': 'PoolManager',
    #              'IMPL': None,
    #              'LOCATION': None,
    #              'MUTABLE': None,
    #              'NAME': None,
    #              'RETURNS': None,
    #              'SIG': '_accountPoolBalanceDelta',
    #              'TYPE': None,
    #              'VISIBLE': None},
    #    'log': '    function _accountPoolBalanceDelta(PoolKey memory key, BalanceDelta delta, address target) internal {',
    #    'rule': 'warning(info-variable)'
    # },]
    output = search("[*].data", output)
    # print(output)

    processed: list[dict] = []
    for o in output:
        processed.extend(parse_args_returns(o))
    # print(processed)

    res = {}
    for p in processed:
        classified = classify_variables(p)
        print(classified)
        _key = classified["NAME"]
        if _key not in res.keys():
            res[_key] = []
        res[_key].append(classified)
    return res


def parse_args_returns(_var: dict) -> list[dict]:
    # {'ARGS': 'PoolKey memory key, uint24 newDynamicLPFee',
    #  'CONTRACT': 'PoolManager',
    #  'IMPL': None,
    #  'LOCATION': None,
    #  'MUTABLE': None,
    #  'NAME': None,
    #  'RETURNS': None,
    #  'SIG': 'updateDynamicLPFee',
    #  'TYPE': None,
    #  'VISIBLE': None}

    _res = []
    _base: dict = {
        "SCOPE": None,
        "CONTRACT": _var["CONTRACT"],
        "SIG": _var["SIG"],
        "LOCATION": _var["LOCATION"],
        "VISIBLE": _var["VISIBLE"],
        "TYPE": _var["TYPE"],
        "MUTABLE": _var["MUTABLE"],
        "NAME": _var["NAME"],
    }

    # TODO: implement 'IMPL' in the next layer

    # parse ARGS and RETURNS to TYPE, LOCATION, NAME
    # do interpolation only for ARGS and RETURNS
    # since information of ARGS and RETURNS are removed while parsing
    if (_var["ARGS"] or _var["RETURNS"]) and _var["NAME"] is None:
        if _var["ARGS"]:
            _var["ARGS"]: list = list(map(str.strip, _var.get("ARGS").split(",")))
            # print(_var.get("ARGS")) # ['PoolKey memory key', 'uint24 newDynamicLPFee']
        if _var["RETURNS"]:
            _var["RETURNS"]: list = list(map(str.strip, _var.get("RETURNS").split(",")))
            # print(_var.get("RETURNS")) # ['Pool.State storage']
        _type_loc_names = (_var["ARGS"] or []) + (_var["RETURNS"] or [])

        for tln in _type_loc_names:
            _split_tln = tln.split(" ")
            is_named_variable = len(_split_tln) > 1
            has_location = len(_split_tln) > 2
            if is_named_variable:
                _base["TYPE"] = _split_tln[0]
                _base["LOCATION"] = _split_tln[1] if has_location else "memory"
                _base["NAME"] = _split_tln[2] if has_location else _split_tln[1]
                if _base["NAME"] in ["memory", "storage", "calldata"]:
                    # TODO: ensure regex not to get the location as a variable name
                    continue
                if tln in _var["ARGS"]:
                    _base["SCOPE"] = "args"
                elif tln in _var["RETURNS"]:
                    _base["SCOPE"] = "returns"
                _res.append(_base.copy())
    elif _base["NAME"] is not None:
        _res.append(_base)
    return _res


def classify_variables(_var: dict) -> dict:
    _base: dict = {
        "NAME": _var["NAME"],
        "SIG": _var["SIG"],
        "SCOPE": None,
        "LOCATION": _var["LOCATION"],
        "VISIBLE": None,
        "TYPE": _var["TYPE"],
        "MUTABLE": _var["MUTABLE"] if _var["MUTABLE"] else "mutable"
    }
    if _var["LOCATION"] == "calldata":
        _base["MUTABLE"] = "immutable"
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
    #       "SCOPE": "function" | "storage" | "inherited",
    #       "LOCATION": $LOCATION,
    #       "VISIBLE" : $VISIBLE,
    #       "TYPE": $TYPE,
    #       "MUTABLE": "mutable" | "immutable" | "constant" | "transient"
    #   },
    # ]}
    if _var["SIG"]:
        _base["SIG"] = f"{_var['CONTRACT']}:{_var['SIG']}"
        _base["SCOPE"] = _var["SCOPE"] if _var["SCOPE"] else "function"
        _base["LOCATION"] = _var["LOCATION"] if _var["LOCATION"] else "memory"
    else:
        # storage scope
        # can be inherited scope, but currently regex finds only explicit declaration cases
        # which means, the scope can be function or storage for now
        _base["SIG"] = _var["CONTRACT"]
        _base["SCOPE"] = "storage"  # TODO: implement 'inherited' in the next layer
        _base["LOCATION"] = _var["LOCATION"] if _var["LOCATION"] else "storage"
        _base["VISIBLE"] = _var["VISIBLE"] if _var["VISIBLE"] else "internal"

    return _base


if __name__ == '__main__':
    _vars = get_variables("code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol")
    # pprint(_vars)
