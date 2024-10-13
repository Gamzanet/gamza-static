from parser.run_semgrep import get_semgrep_output


def test_a():
    # TODO: supports absolute path file reference
    output: list = get_semgrep_output("misconfigured-Hook", "code/0xe8e23e97fa135823143d6b9cba9c699040d51f70.sol")
    print(output)
    assert len(output) >= 1
