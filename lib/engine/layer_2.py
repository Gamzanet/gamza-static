import json
import re
from pprint import pprint

from jmespath import search

from engine.run_semgrep import get_semgrep_output
from extractor.getter import get_conditions
from layers.dataclass.Attributes import Purity, Visibility
from layers.dataclass.Components import Function


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
    with open("out/modifiers.json", "w") as f:
        json.dump(res, f)
    return res


# currently source code should include single contract
# TODO: delegate to Builder
def get_functions(_target_path="code/3.sol") -> list[Function]:
    bodies: list[dict] = get_semgrep_output("info-function-body", _target_path)
    _raw_body = search("[0].data.BODY", bodies)

    # remove from receive & fallback to EOF
    _pattern_to_remove = r"(?:receive|fallback)\s*\(\s*\)[\s\S]+\{[\s\S]+"
    _body_cleansed = re.sub(_pattern_to_remove, "", _raw_body)

    output = get_semgrep_output("info-function", _target_path)
    output = search("[*].data[]", output)

    res = []

    for idx, (_output) in enumerate(output):
        name = _output["SIG"].split("(")[0]

        _has_params = re.search(r"\((.*)\)", _output["SIG"])
        parameters = list(map(str.strip, _has_params.group(1).split(","))) if _has_params else []
        modifiers = _output["MOD"].split(" ") if _output["MOD"] else []

        _pattern_prefix = rf"function\s+{name}\(.*?\).*?"
        _pattern_general = _pattern_prefix + r"(\{[\s\S]+?)\s*function"
        _pattern_end = _pattern_prefix + r"(\{.+)"
        _pattern = _pattern_general if idx != len(output) - 1 else _pattern_end
        _body_pattern = re.search(_pattern, _body_cleansed, flags=re.MULTILINE | re.DOTALL)

        function_body: str = _body_pattern.group(1) if _body_pattern else ""
        # print("name " + name)
        # print("------------")
        # print(function_body)
        # print("------------")
        # print(_pattern, _body["BODY"])

        conditions = get_conditions(function_body)

        res.append(Function(
            name=name,
            parameters=parameters,
            visibility=Visibility.from_str(_output["VIS"]),
            payable=_output["PAY"],
            modifiers=modifiers,
            purity=Purity.from_str(_output["PURITY"]),
            is_override="override" == _output["OVER"],
            returns=_output["RETURN"],
            body=function_body,
            access_control=conditions,
        ))
    return res


def get_variables(_target_path="code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol") -> dict[str, list[dict]]:
    """
    Get the variables of the contract.
    Code should be formatted by the Loader before calling this function.
    :rtype: dict[str, list[dict]]
    :returns: { $variableName: [{ 'NAME', 'SIG', 'SCOPE', 'LOCATION', 'VISIBLE', 'TYPE', 'MUTABLE' }, ...], ... }
    """
    output: list[dict] = get_semgrep_output(
        "info-variable",
        _target_path, use_cache=True)
    output = search("[*].data", output)

    processed: list[dict] = []
    for o in output:
        processed.extend(parse_args_returns(o))
    return aggregate_result_variables(processed)


def aggregate_result_variables(_processed: list[dict]) -> dict:
    res = {}
    for p in _processed:
        classified = classify_variables(p)
        # print(classified)
        _key = classified["NAME"]
        if _key not in res.keys():
            res[_key] = []
        res[_key].append(classified)
    return res


def parse_args_returns(_var: dict) -> list[dict]:
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


# ---------- END OF GET_VARIABLES() RELATED FUNCTIONS ---------- #
# TODO: encapsulate customized Layer-2 rules into a class

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
