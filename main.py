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


# currently source code should include single contract
def get_function_info(_target_path="source/3.sol"):
    # Get the output of the semgrep command
    output: list = get_semgrep_output("info-function", _target_path)
    # pprint(output)

    # [*].data.CONTRACT
    # [*].data.SIG
    # [*].data.VIS
    # [*].data.PAY
    # [*].data.PURITY
    # [*].data.MOD
    # [*].data.RETURN
    res = list(search("[*].data.[*][0]", output))
    # pprint(res)
    return res


if __name__ == "__main__":
    # res = is_valid_hook(_target_path="source/1.sol")
    res = get_function_info(_target_path="source/2.sol")
    pprint(res)
