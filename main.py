from pprint import pprint

from jmespath import search

from lib.run_semgrep import get_semgrep_output


def is_valid_hook(_target_path="source/1.sol"):
    # Get the output of the semgrep command
    output: list = get_semgrep_output("misconfigured-Hook", _target_path)
    pprint(output)

    # group output["data"]["SIG"]
    # group output["data"]["IMPL"]
    # intersect the two groups
    sig = set(search("[*].data.SIG", output))
    # print(sig)
    impl = set(search("[*].data.IMPL", output))
    # print(impl)
    res = sig - impl
    if res:
        print(f"{_target_path}:", ', '.join(res), "is not implemented")
        return False
    return True


if __name__ == "__main__":
    res = is_valid_hook(_target_path="source/1.sol")
    print(res)
