import json

from engine.run_semgrep import get_semgrep_output, parse_emacs_output, parse_message_schema, \
    emacs_tuple_to_dict_with_schema, read_message_schema_by_rule_name, read_rule_by_name
from utils.paths import rule_rel_path_by_name, run_cli_must_succeed, open_with_mkdir


def test_basic():
    _input: list[dict] = get_semgrep_output(
        "info-variable",
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


def test_run_semgrep():
    _rule_path = rule_rel_path_by_name("info-layer2-assignee")
    _target_path = "code/4.sol"
    arg = f"semgrep scan -f rules/{_rule_path} {_target_path} --emacs"
    _out = run_cli_must_succeed(arg, capture_output=True)
    assert len(_out) > 0


def test_parse_result():
    _out = (
        "code/4.sol:37:9:info(info-layer2-assignee):        hookOperator = sender;:DoubleInitHook |&| "
        "beforeInitialize |&| hookOperator |&| sender |;|\n"
        "code/4.sol:49:13:info(info-layer2-assignee):            maxSwapCounter = swapCounter[key.toId("
        ")];:DoubleInitHook |&| beforeSwap |&| maxSwapCounter |&| swapCounter[key.toId()] |;|\n")
    _parsed = parse_emacs_output(_out)
    assert len(_parsed) == 2
    for p in _parsed:
        assert len(p) == 5  # (code, severity, rule, log, message)
    with open_with_mkdir("out/emacs_parsed.txt", "w") as f:
        f.write(str(_parsed))


def test_parse_message_schema():
    _msg_schema_in = "$CONTRACT |&| $SIG |&| $LVALUE |&| $RVALUE |;|"
    _expect = ["CONTRACT", "SIG", "LVALUE", "RVALUE"]
    _actual = parse_message_schema(_msg_schema_in)
    assert _expect == _actual


def test_emacs_tuple_to_dict():
    _out: list[tuple] = [
        ('code/4.sol:37:9', 'info', 'info-layer2-assignee', 'hookOperator = sender;',
         'DoubleInitHook |&| beforeInitialize |&| hookOperator |&| sender '),
        ('code/4.sol:49:13', 'info', 'info-layer2-assignee', 'maxSwapCounter = swapCounter[key.toId()];',
         'DoubleInitHook |&| beforeSwap |&| maxSwapCounter |&| swapCounter[key.toId()] ')]
    _msg_schema = ["CONTRACT", "SIG", "LVALUE", "RVALUE"]

    _expect = [
        {'code': 'code/4.sol:37:9',
         'severity': 'info',
         'rule': 'info-layer2-assignee',
         'log': 'hookOperator = sender;',
         'data': {'CONTRACT': 'DoubleInitHook',
                  'SIG': 'beforeInitialize',
                  'LVALUE': 'hookOperator',
                  'RVALUE': 'sender'},
         },
        {'code': 'code/4.sol:49:13',
         'severity': 'info',
         'rule': 'info-layer2-assignee',
         'log': 'maxSwapCounter = swapCounter[key.toId()];',
         'data': {'CONTRACT': 'DoubleInitHook',
                  'SIG': 'beforeSwap',
                  'LVALUE': 'maxSwapCounter',
                  'RVALUE': 'swapCounter[key.toId()]'}
         }
    ]

    _output = []
    for r in _out:
        _scheme = emacs_tuple_to_dict_with_schema(r, _msg_schema)
        _output.append(_scheme)
    assert _output == _expect


def test_read_rule_by_name():
    # read mapping_ruleName_path.json
    with open("rules/mapping_ruleName_path.json", "r") as f:
        _mapping = json.load(f)
    assert _mapping["root"] == "processed"

    _rules: dict[str, str] = _mapping["class"]

    assert len(_rules.keys()) > 0

    assert _rules["misconfigured-Hook"] == "best-practice"
    assert read_message_schema_by_rule_name("misconfigured-Hook") == "$CONTRACT |&| $SIG |&| $IMPL |;|"

    _rule_meta = read_rule_by_name("misconfigured-Hook")
    assert _rule_meta["severity"] == "WARNING"
    assert _rule_meta["id"] == "misconfigured-Hook"

    assert _rules["missing-onlyPoolManager-modifier"] == "security"
    assert _rules["low_call"] == "security"
    assert _rules["missing_token_transfer_while_burnt"] == "security"
    assert _rules["get_slot0_check"] == "security"
