import os.path
import re
from typing import Generic, TypeVar

from engine.layer_2 import get_variables, get_functions
from extractor.getter import get_contract_name, get_inheritance, get_library, get_license, get_imports, \
    get_solc_version
from layers.Loader import Loader
from layers.dataclass.Attributes import Mutability, Scope, Location, Visibility
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
