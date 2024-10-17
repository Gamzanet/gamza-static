import os

from parser.run_semgrep import get_semgrep_output


def test_misconfigured_hook():
    _cur_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    # TODO: supports absolute path file reference
    output: list = get_semgrep_output("misconfigured-Hook", "code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol")
    print(output)
    os.chdir(_cur_dir)
    assert len(output) >= 1


def test_basic():
    _cur_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.dirname(__file__)))

    _input: list[dict] = get_semgrep_output(
        "info-variable",
        "code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol",
        use_cache=False
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

    os.chdir(_cur_dir)
    assert _input_0["VISIBLE"] == "private"
