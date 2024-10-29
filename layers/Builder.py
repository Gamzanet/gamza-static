import os.path
import re
from typing import Generic, TypeVar

from jmespath import search

from engine.run_semgrep import get_semgrep_output
from extractor.getter import get_contract_name, get_inheritance, get_library, get_license, get_imports, \
    get_solc_version, get_conditions
from layers.Loader import Loader
from layers.dataclass.Attributes import Mutability, Scope, Location, Visibility, Purity
from layers.dataclass.Components import Contract, Function, Variable, Metadata

Buildable = TypeVar('Buildable', Contract, Function, Variable)


class BaseBuilder(Generic[Buildable]):
    def __init__(self):
        self.loader = Loader()

    def build(self, _code) -> str:
        _code = self.loader.remove_comments(_code)
        _path = self.loader.get_cache_path(_code, "sol")
        if not os.path.exists(_path):
            self.loader.overwrite(_path, _code)
        self.loader.format(_path)
        return _path


class MetadataBuilder(BaseBuilder[Metadata]):
    def __init__(self):
        super().__init__()

    def build(self, _code) -> Metadata:
        _path = super().build(_code)
        _code = self.loader.read_code(_path)
        return Metadata(
            chain="unichain",
            evm_version="cancun",
            license=get_license(_code),
            solc_version=get_solc_version(_code)
        )


class ContractBuilder(BaseBuilder[Contract]):
    def __init__(self):
        super().__init__()

    def build(self, _code) -> Contract:
        _path = super().build(_code)
        _code = self.loader.read_code(_path)
        return Contract(
            target_code=_code,
            imports=get_imports(_code),
            inline_code=self.loader.inline_code(_code),
            name=get_contract_name(_code),
            inheritance=get_inheritance(_path),
            library=get_library(_path)
        )


class FunctionBuilder(BaseBuilder[Function]):
    def __init__(self):
        super().__init__()

    def build(self, _code) -> list[Function]:
        _path = super().build(_code)
        # 1. Parser should extract the functions
        _parsed: list[Function] = get_functions(_path)

        # 2. Builder should build the functions
        for _function in _parsed:
            _function.name = _function.name.split("(")[0]
            _function.parameters = _function.parameters if _function.parameters else []
            _function.payable = _function.payable == "payable"
            _function.returns = self.search_small_bracket_and_parse(str(_function.returns))

        return _parsed

    @staticmethod
    def search_small_bracket_and_parse(_target: str, _seperator: str = ",") -> list[str]:
        try:
            _search = re.search(r"\((.*)\)", _target).group(1)
            _parse = list(map(str.strip, re.split(_seperator, _search)))
        except AttributeError:
            _parse = []
        return _parse


class VariableBuilder(BaseBuilder[Variable]):
    def __init__(self):
        super().__init__()

    def build(self, _code) -> list[Variable]:
        _path = super().build(_code)
        # 1. Parser should extract the variables
        _parsed = get_variables(_path)
        # 2. Builder should build the variables
        res = []
        for _name, _variables in _parsed.items():
            for _variable in _variables:
                res.append(
                    Variable(
                        name=_variable["NAME"],
                        signature=_variable["SIG"],
                        type=_variable["TYPE"],
                        location=Location.from_str(_variable["LOCATION"]),
                        visibility=Visibility.from_str(_variable["VISIBLE"]),
                        scope=Scope.from_str(_variable["SCOPE"]),
                        mutability=Mutability.from_str(_variable["MUTABLE"])
                    )
                )
        return res


# currently source code should include single contract
# TODO: delegate to Builder

def get_functions(_target_path="code/3.sol") -> list[Function]:
    bodies: list[dict] = get_semgrep_output("info-function-body", _target_path)
    _raw_body = search("[0].data.BODY", bodies)

    # remove from receive & fallback to EOF
    _pattern_to_remove = r"(?:receive|fallback)\s*\(\s*\)[\s\S]+\{[\s\S]+"
    if _raw_body:
        _body_cleansed = re.sub(_pattern_to_remove, "", _raw_body)
    else:
        _body_cleansed = ""

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
