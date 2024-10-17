import os
from pprint import pprint

from pydantic import BaseModel


class SolidityAuditing(BaseModel):
    class Problem(BaseModel):
        problem_code: list[str]
        what_problem_is: str
        how_to_solve: str
        code_after_fixed: list[str]

    problems: list[Problem]
    has_critical_issue: bool


_rules_applied: str = """
1. given code is written in Solidity
2. when function called, system runs code in a scope
3. scope defines with code in curly braces
4. each operation consumes gas
5. gas is limited
6. for-loop iterates operations
7. too much iteration causes out-of-gas error
8. out-of-gas error leads to DoS which is an availability issue
9. to prevent DoS, limit iteration count
10. modify the code to limit iteration count
11. if loop iterates data structure, keep the length to a minimum

given code:
"""

_sample_code = """
contract TooMuchGasHook is Counter {
    uint256 private tmp;

    constructor(IPoolManager _poolManager) Counter(_poolManager) {}

    function beforeSwap(
        address sender,
        PoolKey calldata key,
        IPoolManager.SwapParams calldata params,
        bytes calldata data
    ) public override returns (bytes4, BeforeSwapDelta, uint24) {
        for (uint256 i = 0; i < 1e6; i++) {
            tmp += i;
        }
        return super.beforeSwap(sender, key, params, data);
    }
}
"""

_instruction_template = """
you are an auditor for a Solidity smart contract.
you are tasked to review the given code.
you need to identify and fix any potential security issues.
follow the given rules to identify the issues.
if you find any issue, provide a solution how to fix it.
you can modify the code to fix the issue if necessary.
"""


def test():
    # 1. model gets code with context
    # 2. model generates answer
    # 3. 코드로 발생할 수 있는 위협: 학습 데이터로 주어져야 함
    # 4. 해결 방안: 까지는 학습 데이터로 주어져야 함
    # 5. 코드 수정
    from openai import OpenAI
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        organization=os.environ.get("OPENAI_ORGANIZATION"),
        project=os.environ.get("OPENAI_PROJECT"),
    )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": _instruction_template},
            {
                "role": "user",
                "content": _rules_applied + _sample_code
            }
        ],
        response_format=SolidityAuditing,
    ).model_dump_json()
    with open("response.json", "w") as f:
        f.write(completion)
    pprint(completion)
