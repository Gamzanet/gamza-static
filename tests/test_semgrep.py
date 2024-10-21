from parser.run_semgrep import get_semgrep_output
from utils.paths import rule_rel_path_by_name


def test_basic():
    _input: list[dict] = get_semgrep_output(
        rule_rel_path_by_name("info-variable"),
        "code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol",
        use_cache=True
    )

    _input_0: dict = _input[0]["data"]

    """
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
    """  # pprint(_input_0)

    assert _input_0["VISIBLE"] == "private"
