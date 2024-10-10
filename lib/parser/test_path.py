from parser.run_semgrep import get_semgrep_output


def test_a():
    # TODO: supports absolute path file reference
    output: list = get_semgrep_output("misconfigured-Hook", "code/1.sol")
    print(output)
    assert len(output) >= 1
