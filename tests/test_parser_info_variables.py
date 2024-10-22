from rich.pretty import pprint

import parser.layer_2


def test_get_variables():
    res = parser.layer_2.get_variables(
        _target_path="code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol",
    )
    assert res != {}
    pprint(res)


def test_scope_storage():
    with open("code/json/info-variable_code-0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol.json", "r") as f:
        _input: dict = parser.layer_2.json.load(f)["data"]
    _input: list[dict] = parser.layer_2.search("[*].data[]", _input)

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

    _output_0: list[dict] = parser.layer_2.parse_args_returns(_input[0])
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

    _result_0_0 = parser.layer_2.classify_variables(_output_0_0)
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
    with open("code/json/info-variable_code-0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol.json", "r") as f:
        _input: dict = parser.layer_2.json.load(f)["data"]
    _input: list[dict] = parser.layer_2.search("[*].data[]", _input)

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

    _output_6: list[dict] = parser.layer_2.parse_args_returns(_input[6])
    assert len(_output_6) == 1
    _output_6_0: dict = _output_6[0]

    assert _output_6_0 == {
        'CONTRACT': 'PoolManager',
        'LOCATION': None,
        'MUTABLE': None,
        'NAME': 'principalDelta',
        'SCOPE': None,
        'SIG': 'modifyLiquidity',
        'TYPE': 'BalanceDelta',
        'VISIBLE': None
    }

    _result_6_0 = parser.layer_2.classify_variables(_output_6_0)
    assert _result_6_0 == {
        "LOCATION": "memory",
        "MUTABLE": "mutable",
        "NAME": "principalDelta",
        "SCOPE": "function",
        "SIG": "PoolManager:modifyLiquidity",
        "TYPE": "BalanceDelta",
        "VISIBLE": None,
    }


def test_scope_function_calldata_immutable():
    with open("code/json/info-variable_code-0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol.json", "r") as f:
        _input: dict = parser.layer_2.json.load(f)["data"]
    _input: list[dict] = parser.layer_2.search("[*].data[]", _input)

    """ INPUT
    {'ARGS': 'PoolKey memory key,\n'
             '        IPoolManager.ModifyLiquidityParams memory params,\n'
             '        bytes calldata hookData',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': 'BalanceDelta callerDelta, BalanceDelta feesAccrued',
     'SIG': 'modifyLiquidity',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[5])

    _output_5: list[dict] = parser.layer_2.parse_args_returns(_input[5])
    assert len(_output_5) == 3 + 2  # 3 args, 2 returns
    _output_5_2: dict = _output_5[2]

    assert _output_5_2 == {
        'CONTRACT': 'PoolManager',
        'LOCATION': 'calldata',
        'MUTABLE': None,
        'NAME': 'hookData',
        'SCOPE': 'args',
        'SIG': 'modifyLiquidity',
        'TYPE': 'bytes',
        'VISIBLE': None
    }

    _result_5_2 = parser.layer_2.classify_variables(_output_5_2)
    assert _result_5_2 == {
        'LOCATION': 'calldata',
        'MUTABLE': 'immutable',
        'NAME': 'hookData',
        'SCOPE': 'args',
        'SIG': 'PoolManager:modifyLiquidity',
        'TYPE': 'bytes',
        'VISIBLE': None
    }


def test_scope_function_parsing_args_returns():
    with open("code/json/info-variable_code-0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol.json", "r") as f:
        _input: dict = parser.layer_2.json.load(f)["data"]
    _input: list[dict] = parser.layer_2.search("[*].data[]", _input)

    """ INPUT
    {'ARGS': 'PoolKey memory key, uint24 newDynamicLPFee',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': None,
     'SIG': 'updateDynamicLPFee',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[22])

    _output_22: list[dict] = parser.layer_2.parse_args_returns(_input[22])
    assert len(_output_22) == 2 + 0  # 2 args, 0 returns


def test_scope_global_duplicated_name_listing():
    with open("code/json/info-variable_code-0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol.json", "r") as f:
        _input: dict = parser.layer_2.json.load(f)["data"]
    _input: list[dict] = parser.layer_2.search("[*].data[]", _input)

    """ INPUT
    {'ARGS': 'PoolKey memory key, uint160 sqrtPriceX96',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': 'int24 tick',
     'SIG': 'initialize',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[4])
    """ INPUT
    {'ARGS': 'PoolKey memory key,\n'
             '        IPoolManager.ModifyLiquidityParams memory params,\n'
             '        bytes calldata hookData',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': 'BalanceDelta callerDelta, BalanceDelta feesAccrued',
     'SIG': 'modifyLiquidity',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[5]
    """ INPUT
    {'ARGS': 'PoolKey memory key, IPoolManager.SwapParams memory params, bytes '
             'calldata hookData',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': 'BalanceDelta swapDelta',
     'SIG': 'swap',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[8])
    """ INPUT
    {'ARGS': 'PoolKey memory key, uint256 amount0, uint256 amount1, bytes calldata '
             'hookData',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': 'BalanceDelta delta',
     'SIG': 'donate',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[14])
    """ INPUT
    {'ARGS': 'PoolKey memory key, uint24 newDynamicLPFee',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': None,
     'SIG': 'updateDynamicLPFee',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[22])
    """ INPUT
    {'ARGS': 'PoolKey memory key, BalanceDelta delta, address target',
     'CONTRACT': 'PoolManager',
     'IMPL': None,
     'LOCATION': None,
     'MUTABLE': None,
     'NAME': None,
     'RETURNS': None,
     'SIG': '_accountPoolBalanceDelta',
     'TYPE': None,
     'VISIBLE': None}
    """  # pprint(_input[25])

    _output_4: list[dict] = parser.layer_2.parse_args_returns(_input[4])
    _output_5: list[dict] = parser.layer_2.parse_args_returns(_input[5])
    _output_8: list[dict] = parser.layer_2.parse_args_returns(_input[8])
    _output_14: list[dict] = parser.layer_2.parse_args_returns(_input[14])
    _output_22: list[dict] = parser.layer_2.parse_args_returns(_input[22])
    _output_25: list[dict] = parser.layer_2.parse_args_returns(_input[25])

    assert len(_output_4) == 2 + 1  # 2 args, 1 returns
    assert len(_output_5) == 3 + 2  # 3 args, 2 returns
    assert len(_output_8) == 3 + 1  # 3 args, 1 returns
    assert len(_output_14) == 4 + 1  # 4 args, 1 returns
    assert len(_output_22) == 2 + 0  # 2 args, 0 returns
    assert len(_output_25) == 3 + 0  # 3 args, 0 returns

    _outputs_key: list[dict] = _output_4 + _output_5 + _output_8 + _output_14 + _output_22 + _output_25
    _unique_names = list(parser.layer_2.search("[*].NAME", _outputs_key))
    # 22 variable usage in total where
    #     variable name `key` is duplicated for 6 times
    #     variable name `hookData` is duplicated for 3 times
    #     variable name `params` is duplicated for 2 times
    #     variable name `delta` is duplicated for 2 times
    # which makes 13 unique names

    _result_key = parser.layer_2.aggregate_result_variables(_outputs_key)
    assert len(_result_key) == 22 - 5 - 2 - 1 - 1
    assert len(_result_key["key"]) == 6
    assert len(_result_key["hookData"]) == 3
    assert len(_result_key["params"]) == 2
    assert len(_result_key["delta"]) == 2
