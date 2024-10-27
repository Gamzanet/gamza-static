import attr

from engine.lexer import Condition
from layers import Builder
from layers.dataclass.Attributes import Purity, Visibility
from layers.dataclass.Components import Variable


@attr.s(auto_attribs=True)
class ResultScope:
    name: str
    variable: list[Variable]


@attr.s(auto_attribs=True)
class ContractScope(ResultScope):
    functions: list[str]
    libraries: list[str]


@attr.s(auto_attribs=True)
class FunctionScope(ResultScope):
    parameters: list[Variable]
    purity: Purity
    visibility: Visibility
    payable: bool
    override: bool
    modifier: list[str]
    returns: list[Variable]
    body: str
    access_control: list[Condition]


@attr.s(auto_attribs=True)
class FileScope:
    file_name: str
    license: str
    solc_version: str
    imports: list[str]
    contract_scope: ContractScope
    function_scopes: list[FunctionScope]


@attr.s(auto_attribs=True)
class CodeAnalysisAggregation:
    chain_name: str
    evm_version: str
    data: FileScope  # assume single contract


class Aggregator:

    def __init__(self):
        self.metadata_builder = Builder.MetadataBuilder()
        self.contract_builder = Builder.ContractBuilder()
        self.function_builder = Builder.FunctionBuilder()
        self.variable_builder = Builder.VariableBuilder()

    def aggregate(self, code: str) -> CodeAnalysisAggregation:
        """
        This function is designed for aggregating all informative analysis results, especially handled in layer 2.
        This function focus on handling user customized rules, which use variety of different message schemas.
        """
        metadata = self.metadata_builder.build(code)
        contract = self.contract_builder.build(code)
        functions = self.function_builder.build(code)
        variables = self.variable_builder.build(code)

        function_names = [f.name for f in functions]
        storage_variables = [v for v in variables if v.location == "storage"]
        function_variables = [v for v in variables if v.location in ["memory", "calldata"]]

        return CodeAnalysisAggregation(
            chain_name=metadata.chain,
            evm_version=metadata.evm_version,
            data=FileScope(
                license=metadata.license,
                solc_version=metadata.solc_version,
                imports=contract.imports,
                file_name=contract.name,
                contract_scope=ContractScope(
                    name=contract.name,
                    variable=storage_variables,
                    functions=function_names,
                    libraries=contract.library
                ),
                function_scopes=[
                    FunctionScope(
                        name=f.name,
                        purity=f.purity,
                        visibility=f.visibility,
                        payable=f.payable,
                        override=f.is_override,
                        body=f.body,
                        variable=[v for v in function_variables if v.signature.split(":")[-1] == f.name],
                        modifier=f.modifiers,
                        access_control=f.access_control,
                        parameters=[v for v in function_variables if
                                    v.signature.split(":")[-1] == f.name and v.scope == "args"],
                        returns=[v for v in function_variables if
                                 v.signature.split(":")[-1] == f.name and v.scope == "returns"],

                    ) for f in functions
                ]
            )
        )
