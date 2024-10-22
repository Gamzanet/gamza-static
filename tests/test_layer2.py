import parser.layer_2


def test_parser_info_layer2():
    _res = parser.layer_2.detect_storage_overwrite_in_multi_pool_initialization(
        _target_path="code/4.sol"
    )
    assert _res != {}
    print(_res)
