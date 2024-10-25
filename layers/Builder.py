from jmespath import search

from parser.run_semgrep import get_semgrep_output
from utils.paths import rule_rel_path_by_name


def test_info_inheritance():
    _code_rel_path = "code/2.sol"
    res = get_semgrep_output(
        rule_rel_path_by_name("info-inheritance"),
        _code_rel_path
    )
    assert (search("[*].data.INHERIT", res)
            == ["BaseHook", "someOtherContract"])
