from extractor.getter import get_conditions


def test_parse_if_else():
    print()
    _given = open("code/1.sol", "r").read()

    for cond in get_conditions(_given):
        print(cond)
