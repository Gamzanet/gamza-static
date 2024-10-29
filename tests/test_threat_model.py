from layers.Aggregator import ThreatModelBase
from layers.dataclass.Components import SimpleDetectionLog, ContractScope, FunctionScope, FileScope


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
