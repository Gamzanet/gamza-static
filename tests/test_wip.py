from engine.layer_2 import detect_storage_overwrite_in_multi_pool_initialization
from extractor.getter import get_conditions


def test_parse_if_else():
    print()
    _given = open("code/1.sol", "r").read()

    for cond in get_conditions(_given):
        print(cond)


def test_parser_info_layer2():
    _res = detect_storage_overwrite_in_multi_pool_initialization(
        _target_path="code/4.sol"
    )
    assert _res != {}
    print(_res)
