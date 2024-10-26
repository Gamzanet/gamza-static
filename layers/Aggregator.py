from layers.Builder2 import Builder
from layers.dataclass.Components import Metadata, Contract


# 5. 이후 추가적으로 필요한 custom semgrep rules 돌리기 (전처리기 이전에 수행하는게 맞음) ㅡ 차라리 condition 확인을 l2 함수로 만들면 됨
# 6. conditions는 현재 contract 기준으로 구현되어 있는데 이제 각각의 함수 컨텍스트 안에서 실행해야함
#     1. ㅁㅣ리 만들어둔 전처리기로 클린업
#     2. 토크나이저로 토큰화
#     3. Parse로 파싱
#         1. 원래라면 다시 평문화 안 하겠지만 이미 구현해둔거 때뭉에 평문화
#     4. Lexer 돌리기

class Aggregator:
    """
    This class designed for aggregating all informative analysis results, especially handled in layer 2.
    This class focus on handling user customized rules, which use variety of different message schemas.
    """

    def __init__(self):
        self.metadata: Metadata = Metadata(
            chain="unichain",
            evm_version="cancun"
        )
        self.builder: Builder = Builder({

        })
        self.contracts: dict[str, Contract] = {}

    def add_contract(self, code: str):
        self.contracts[str(contract)] = Contract(code)

    def get_functions(self, key: Contract | str):
        if type(key) == Contract:
            key = str(key)
        raise NotImplementedError
