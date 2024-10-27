import json

from attr import asdict

from layers.Aggregator import Aggregator
from layers.Loader import Loader


def test_aggregator_1():
    file_name = "DoubleInitHook"
    code = Loader().read_code(f"{file_name}.sol")
    aggregator = Aggregator()
    res = aggregator.aggregate(code)

    assert res.chain_name == "unichain"
    assert res.evm_version == "cancun"
    assert res.data.file_name == file_name
    assert res.data.license == "UNLICENSED"
    assert res.data.solc_version == "0.8.13"
    assert len(res.data.imports) == 0
    assert res.data.contract_scope.name == "DoubleInitHook"

    assert len(res.data.contract_scope.variable) == 3  # 3 storage variables
    assert len(res.data.contract_scope.functions) == 4  # ignore receive / fallback
    assert len(res.data.contract_scope.libraries) == 0  # no library used
    assert len(res.data.function_scopes) == 4  # ignore receive / fallback

    assert res.data.function_scopes[0].name == "getHookPermissions"
    assert len(res.data.function_scopes[0].variable) == 0
    assert len(res.data.function_scopes[0].modifier) == 0
    assert len(res.data.function_scopes[0].access_control) == 0

    assert res.data.function_scopes[1].name == "beforeInitialize"
    assert len(res.data.function_scopes[1].variable) == 1  # only named variables in args
    assert len(res.data.function_scopes[1].modifier) == 0
    assert len(res.data.function_scopes[1].access_control) == 1  # require(hookOperator == address(0))

    assert res.data.function_scopes[2].name == "beforeSwap"
    assert len(res.data.function_scopes[2].variable) == 1  # only named variables in args
    assert len(res.data.function_scopes[2].modifier) == 0
    assert len(res.data.function_scopes[2].access_control) == 0

    assert res.data.function_scopes[3].name == "withdrawAll"
    assert len(res.data.function_scopes[3].variable) == 0  # cannot detect implicit declaration
    assert len(res.data.function_scopes[3].modifier) == 0
    assert len(res.data.function_scopes[3].access_control) == 2

    json.dump(asdict(res, recurse=True), open(f"out/{file_name}.json", "w"), indent=4)


def test_aggregator_2():
    file_name = "1"
    code = Loader().read_code(f"{file_name}.sol")
    aggregator = Aggregator()
    res = aggregator.aggregate(code)

    assert res.chain_name == "unichain"
    assert res.evm_version == "cancun"
    assert res.data.file_name == "Test"  # code driven analysis default to contract name
    assert res.data.license == "MIT"
    assert res.data.solc_version == "0.8.0"

    assert len(res.data.imports) == 0
    assert res.data.contract_scope.name == "Test"
    assert len(res.data.contract_scope.variable) == 0
    assert len(res.data.contract_scope.functions) == 1
    assert len(res.data.contract_scope.libraries) == 0
    assert len(res.data.function_scopes) == 1

    assert res.data.function_scopes[0].name == "a"
    assert len(res.data.function_scopes[0].variable) == 0  # line should end up with a semicolon
    assert len(res.data.function_scopes[0].modifier) == 0
    assert len(res.data.function_scopes[0].access_control) == 6  # 3 revert, 2 assert, 1 require

    json.dump(asdict(res, recurse=True), open(f"out/{file_name}.json", "w"), indent=4)
