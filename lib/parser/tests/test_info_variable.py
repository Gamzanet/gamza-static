import json

from jmespath import search

from parser.layer_2 import parse_args_returns, classify_variables


def test_scope_storage():
    with open("tests/data/info-variable_code-0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol.json", "r") as f:
        _input: dict = json.load(f)["data"]
    _input: list[dict] = search("[*].data[]", _input)

    """ INPUT
    {'ARGS': None,
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': 'constant',
     'NAME': 'MAX_TICK_SPACING',
     'RETURNS': None,
     'SIG': None,
     'TYPE': 'int24',
     'VISIBLE': 'private'}
    """  # pprint(_input[0])

    _output_0: list[dict] = parse_args_returns(_input[0])
    assert len(_output_0) == 1
    _output_0_0: dict = _output_0[0]

    _key_dropped = ["ARGS", "RETURNS", "IMPL"]
    _key_added = ["SCOPE"]
    for k in _key_dropped:
        assert k not in _output_0_0.keys()
    for k in _key_added:
        assert k in _output_0_0.keys()
    for k, v in _output_0_0.items():
        if k in _key_added:
            assert k not in _input[0].keys()
            continue
        assert _output_0_0[k] == _input[0][k]

    """ OUTPUT
    {'CONTRACT': 'PoolManager',
     'LOCATION': None,
     'MUTABLE': 'constant',
     'NAME': 'MAX_TICK_SPACING',
     'SCOPE': None,
     'SIG': None,
     'TYPE': 'int24',
     'VISIBLE': 'private'}
    """  # pprint(_output_0_0)

    _result_0_0 = classify_variables(_output_0_0)
    assert _result_0_0 == {
        "LOCATION": "storage",
        "MUTABLE": "constant",
        "NAME": "MAX_TICK_SPACING",
        "SCOPE": "storage",
        "SIG": "PoolManager",
        "TYPE": "int24",
        "VISIBLE": "private",
    }


def test_scope_function_explicit_declaration():
    with open("tests/data/info-variable_code-0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol.json", "r") as f:
        _input: dict = json.load(f)["data"]
    _input: list[dict] = search("[*].data[]", _input)

    """ INPUT
    {'ARGS': None,
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': 'principalDelta',
     'RETURNS': None,
     'SIG': 'modifyLiquidity',
     'TYPE': 'BalanceDelta',
     'VISIBLE': None}
    """  # pprint(_input[6])

    _output_6: list[dict] = parse_args_returns(_input[6])
    assert len(_output_6) == 1
    _output_6_0: dict = _output_6[0]

    _key_dropped = ["ARGS", "RETURNS", "IMPL"]
    _key_added = ["SCOPE"]
    for k in _key_dropped:
        assert k not in _output_6_0.keys()
    for k in _key_added:
        assert k in _output_6_0.keys()
    for k, v in _output_6_0.items():
        if k in _key_added:
            assert k not in _input[6].keys()
            continue
        assert _output_6_0[k] == _input[6][k]

    """ OUTPUT
    {'CONTRACT': 'PoolManager',
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': 'principalDelta',
     'SCOPE': None,
     'SIG': 'modifyLiquidity',
     'TYPE': 'BalanceDelta',
     'VISIBLE': None}
    """  # pprint(_output_6_0)

    _result_6_0 = classify_variables(_output_6_0)
    assert _result_6_0 == {
        "LOCATION": "memory",
        "MUTABLE": "mutable",
        "NAME": "principalDelta",
        "SCOPE": "function",
        "SIG": "PoolManager:modifyLiquidity",
        "TYPE": "BalanceDelta",
        "VISIBLE": None,
    }
