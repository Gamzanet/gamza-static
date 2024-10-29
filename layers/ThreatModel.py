from typing import Union, Callable

import attrs

from engine.run_semgrep import run_semgrep_one
from layers.Aggregator import FileScope, FunctionScope, ContractScope, CodeAnalysisAggregation, Aggregator
from layers.Loader import Loader


@attrs.define(init=True, auto_attribs=True)
class DetectionLog:
    title: any
    summary: str
    description: str
    impact: str
    severity: str
    recommendation: str | None
    scopes: list[FileScope | ContractScope | FunctionScope]


@attrs.frozen(auto_attribs=True)
class SlitherData:
    description: str
    impact: str


@attrs.frozen(auto_attribs=True)
class SimpleDetectionLog:
    detector: str
    data: SlitherData

    @staticmethod
    def from_log(log: DetectionLog):
        return SimpleDetectionLog(
            detector=log.summary,
            data=SlitherData(
                description=log.description,
                impact=log.impact
            )
        )


@attrs.define(init=False, auto_attribs=True)
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
            if self.target_scope is FunctionScope:
                self.rule = lambda scope, code: (
                    [run_semgrep_one(rule, self.loader.cache_content(_scope.body, "sol")) for _scope in scope])
            else:
                # TODO: make body for each scope
                self.rule = lambda scope, code: run_semgrep_one(rule, self.loader.cache_content(code, "sol"))
        elif callable(rule):
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


@attrs.frozen(auto_attribs=True)
class ThreatDetectionResult:
    info: CodeAnalysisAggregation
    threats: list[DetectionLog]


def test_model_metadata_override():
    model = ThreatModelBase("function")
    model.mount_rule(lambda scope, code: True)
    model.override_metadata(
        title="Check if the contract contains msg.sender1",
        summary="detector",
        description="description",
        impact="impact",
        severity="Check if the contract contains msg.sender5",
        recommendation="Check if the contract contains msg.sender6"
    )
    log = model.run("contract Example { function foo() public {  } }")
    log = SimpleDetectionLog.from_log(log)
    assert log.detector == "detector"
    assert log.data.description == "description"
    assert log.data.impact == "impact"


def test_threat_model_base_init():
    assert ThreatModelBase("contract").target_scope == ContractScope
    assert ThreatModelBase("file").target_scope == FileScope
    assert ThreatModelBase("function").target_scope == FunctionScope

    try:
        ThreatModelBase("invalid")
        assert False
    except ValueError:
        pass


def test_new_custom_rule():
    def is_contains_msg_sender(scopes: list[FunctionScope], code: str = None) -> bool:
        for scope in scopes:
            for _cond in scope.access_control:
                if not _cond.logic:
                    continue
                if "msg.sender" in _cond.logic:
                    return True
        return False

    model = ThreatModelBase("function")
    model.mount_rule(is_contains_msg_sender)

    print(model.run("contract Example { function foo() public {  } }"))
    print(model.run("contract Example { function foo() public { require(msg.sender == owner); } }"))
    print(model.run(
        "contract Example { function foo() public { require(msg.sender == owner); } function bar() public { require(msg.sender == owner); } }"))


def test_semgrep_rule():
    model = ThreatModelBase("function")
    model.mount_rule("misconfigured-Hook")

    print(model.run("contract ExampleHook is BaseHook { }"))
    print(model.run("contract ExampleHook is BaseHook { function foo() public { } }"))
    print(model.run("contract ExampleHook is BaseHook { function foo() public { require(msg.sender == owner); } }"))
