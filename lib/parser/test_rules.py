from parser.run_semgrep import get_semgrep_output


def test_a():
    # TODO: supports absolute path file reference
    output: list = get_semgrep_output("misconfigured-Hook", "code/1.sol")
    print(output)
    assert len(output) >= 1

#
# def test_preprocess():
#     _input: dict = {'CONTRACT': 'PoolManager', 'SIG': 'modifyLiquidity',
#                     'ARGS': 'PoolKey memory key,\n        IPoolManager.ModifyLiquidityParams memory params,\n        '
#                             'bytes calldata hookData',
#                     'RETURNS': 'BalanceDelta callerDelta, BalanceDelta feesAccrued', 'IMPL': None, 'TYPE': None,
#                     'LOCATION': None, 'VISIBLE': None, 'MUTABLE': None, 'NAME': None}
#     _input: list[dict] = [{"data": _input}]
#     _out: dict = pre_process_atomic_var(_input)[0]
#     for k, v in _out.items():
#         if k in ["ARGS", "RETURNS"]:
#             assert _out.get("ARGS") == ['PoolKey memory key', 'IPoolManager.ModifyLiquidityParams memory params',
#                                         'bytes calldata hookData']
#             assert _out.get("RETURNS") == ['BalanceDelta callerDelta', 'BalanceDelta feesAccrued']
#         else:
#             assert _out.get(k) == _input[0].get("data").get(k)
#
#
# def test_classify_function_scope():
#     _input: dict = {
#         'CONTRACT': 'PoolManager', 'SIG': 'modifyLiquidity',
#         'ARGS': 'PoolKey memory key, IPoolManager.ModifyLiquidityParams memory params, bytes calldata hookData',
#         'RETURNS': 'BalanceDelta callerDelta, BalanceDelta feesAccrued',
#         'IMPL': None, 'TYPE': None,
#         'LOCATION': None, 'VISIBLE': None, 'MUTABLE': None, 'NAME': None
#     }
#
#     _processed = pre_process_atomic_var([{"data": _input}])
#
#     _out = {}
#     for e in _processed:
#         c = classify_variables(e)
#         _out[c.get("name")] = c
#
#     for k, v in _out.items():
#         # {'SIG': 'PoolManager:modifyLiquidity', 'SCOPE': 'function', 'LOCATION': 'memory', 'VISIBLE': 'internal', 'TYPE': None, 'MUTABLE': 'mutable'}
#         assert _out[k].get("SIG") == "PoolManager:modifyLiquidity"
#         assert _out[k].get("SCOPE") == "function"
#         assert _out[k].get("VISIBLE") is None
#         # TODO: modify impl to follow function's visibility
#         # 1. modify rule regex to capture visibility
#         # 2. simply copy the extracted value
#         # for later impl, consider using function call dependency to infer visibility
#
#     from pprint import pprint
#     pprint(_out)
#
#     assert _out.get("callerDelta").get("LOCATION") == "memory"
#     assert _out.get("feesAccrued").get("LOCATION") == "memory"
#     assert _out.get("key").get("LOCATION") == "memory"
#     assert _out.get("params").get("LOCATION") == "memory"
#     assert _out.get("hookData").get("LOCATION") == "calldata"
#
#     assert _out.get("callerDelta").get("TYPE") == "BalanceDelta"
#     assert _out.get("feesAccrued").get("TYPE") == "BalanceDelta"
#     assert _out.get("key").get("TYPE") == "PoolKey"
#     assert _out.get("params").get("TYPE") == "IPoolManager.ModifyLiquidityParams"
#     assert _out.get("hookData").get("TYPE") == "bytes"
#
#     assert _out.get("callerDelta").get("MUTABLE") == "mutable"
#     assert _out.get("feesAccrued").get("MUTABLE") == "mutable"
#     assert _out.get("key").get("MUTABLE") == "mutable"
#     assert _out.get("params").get("MUTABLE") == "mutable"
#     assert _out.get("hookData").get("MUTABLE") == "immutable"
#
#
# def test_classify_storage_scope():
#     _input: dict = {'CONTRACT': 'PoolManager', 'SIG': None, 'ARGS': None, 'RETURNS': None, 'IMPL': None,
#                     'TYPE': 'int24', 'LOCATION': None, 'VISIBLE': 'private', 'MUTABLE': 'constant',
#                     'NAME': 'MIN_TICK_SPACING'}
#     _out = classify_variables(_input)
#
#     assert _out["MIN_TICK_SPACING"]["TYPE"] == "int24"
#     assert _out["MIN_TICK_SPACING"]["SCOPE"] == "storage"
#     assert _out["MIN_TICK_SPACING"]["LOCATION"] == "storage"
#     assert _out["MIN_TICK_SPACING"]["MUTABLE"] == "constant"
#     assert _out["MIN_TICK_SPACING"]["VISIBLE"] == "private"
#
#
# def test_classify_inherit_scope():
#     _input: dict = {'CONTRACT': 'PoolManager', 'SIG': 'unlock', 'ARGS': 'bytes calldata data',
#                     'RETURNS': 'bytes memory result',
#                     'IMPL': None, 'TYPE': None, 'LOCATION': None, 'VISIBLE': None, 'MUTABLE': None, 'NAME': None}
#
#     _out = classify_variables(_input)
#
#     assert _out["data"]["TYPE"] == "bytes"
#     assert _out["data"]["SCOPE"] == "inherited"
#     assert _out["data"]["LOCATION"] == "calldata"
#     assert _out["data"]["MUTABLE"] == "immutable"
#     assert _out["data"]["VISIBLE"] == "public"
#
#     assert _out["result"]["TYPE"] == "bytes"
#     assert _out["result"]["SCOPE"] == "inherited"
#     assert _out["result"]["LOCATION"] == "memory"
#     assert _out["result"]["MUTABLE"] == "mutable"
#     assert _out["result"]["VISIBLE"] == "public"
