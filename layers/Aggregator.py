from typing import Union, Callable

import attr
import attrs

from engine.run_semgrep import run_semgrep_one
from layers import Builder
from layers.Loader import Loader
from layers.dataclass.Components import FileScope, ContractScope, DetectionLog, FunctionScope, SimpleDetectionLog


@attr.s(auto_attribs=True)
class CodeAnalysisAggregation:
    chain_name: str
    evm_version: str
    data: FileScope  # assume single contract


@attrs.define(auto_attribs=True)
class ThreatDetectionResult:
    info: CodeAnalysisAggregation
    threats: list[DetectionLog | SimpleDetectionLog]


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


class ThreatModelBase:
    loader: Loader
    target_scope: FileScope | ContractScope | FunctionScope
    title: str
    summary: str
    description: str
    impact: str  # TODO: enum
    severity: str  # TODO: enum
    recommendation: str | None
    rule: callable

    def __init__(self, target_scope: str | FileScope | ContractScope | FunctionScope):
        self.override_metadata()
        self.loader = Loader()
        if type(target_scope) is str:
            target_scope = target_scope.lower()
            patterns = {
                "file": FileScope,
                "contract": ContractScope,
                "function": FunctionScope
            }
            if target_scope not in patterns:
                raise ValueError("Invalid target scope")
            self.target_scope = patterns[target_scope]
        # else check if target_scope is a subclass of each of the three classes
        elif target_scope in [FileScope, ContractScope, FunctionScope]:
            self.target_scope = target_scope
        else:
            raise ValueError("Invalid target scope")

    # rule can be defined as a semgrep rule name or a custom function
    # semgrep rule runs on the target scope source code
    # custom function runs on attributes which takes the target scope as an argument
    def mount_rule(self, rule: Union[str, Callable]):
        if isinstance(rule, str):
            # semgrep rule
            if self.target_scope is FunctionScope:
                self.rule = lambda scope, code: (
                    True in [run_semgrep_one(rule, self.loader.cache_content(_scope.body, "sol")) for _scope in scope])
            else:
                def run_semgrep_on_target(scope, code):
                    _path = self.loader.cache_content(code, "sol")
                    self.loader.format(_path)
                    return True if run_semgrep_one(rule, _path) else False

                self.rule = run_semgrep_on_target
        elif callable(rule):
            # custom function
            # this params forced because the rule function must accept the target scope as an argument
            self.rule = lambda scope, code: rule(scope, code)
        else:
            raise ValueError("Invalid rule type")

    def override_metadata(
        self,
        title: str = None,
        summary: str = None,
        description: str = None,
        impact: str = None,
        severity: str = None,
        recommendation: str = None
    ):
        self.title = title
        self.summary = summary
        self.description = description
        self.impact = impact
        self.severity = severity
        self.recommendation = recommendation

    def run(self, code: str) -> DetectionLog:
        base_log = DetectionLog(
            title=self.title,
            summary=self.summary,
            description=self.description,
            impact=self.impact,
            severity=self.severity,
            recommendation=self.recommendation,
            scopes=[]
        )

        res = base_log.scopes
        _agg = Aggregator().aggregate(code)
        if self.target_scope is FunctionScope:
            for _scope in _agg.data.function_scopes:
                if self.rule(_agg.data.function_scopes, _scope.body):
                    res.append(_scope)

        elif self.target_scope is ContractScope:
            if self.rule(_agg.data.contract_scope, code):
                res.append(_agg.data.contract_scope)

        elif self.target_scope is FileScope:
            if self.rule(_agg.data, code):
                res.append(_agg.data)
        else:
            raise ValueError("Invalid target scope")
        return base_log
