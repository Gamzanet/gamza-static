from rich.pretty import pprint

from parser.layer_2 import get_variables


def test_get_variables():
    res = get_variables(
        _target_path="code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol"
    )
    assert res != {}
    pprint(res)
