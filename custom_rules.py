from engine.layer_2 import is_valid_hook
from layers.Aggregator import ThreatModelBase
from layers.Loader import Loader
from layers.dataclass.Components import FunctionScope, ContractScope


def model_missing_token_transfer_while_burnt() -> ThreatModelBase:
    model = ThreatModelBase("contract")
    model.mount_rule("missing_token_transfer_while_burnt")
    model.override_metadata(
        summary="Missing token transfer while burnt",
        description="Not calling _burn function for token after/before the transfer in redeem function, could be dangerous.",
        impact="medium"
    )
    return model


def model_get_slot0_check() -> ThreatModelBase:
    model = ThreatModelBase("contract")
    model.mount_rule("get_slot0_check")
    model.override_metadata(
        summary="Using Slot0 directly to return price data as an oracle",
        description="Using Slot0 directly to return price data as an oracle, can be vulnerable at price oracle manipulation",
        impact="low"
    )
    return model


def model_low_call() -> ThreatModelBase:
    model = ThreatModelBase("contract")
    model.mount_rule("low_call")
    model.override_metadata(
        summary="Low call",
        description="The hook is low-calling to other addresses, which can be operated as a malcious contract.",
        impact="information"
    )
    return model


def model_missing_only_pool_manager_modifier() -> ThreatModelBase:
    model = ThreatModelBase("contract")
    model.mount_rule("missing-onlyPoolManager-modifier")
    model.override_metadata(
        summary="Missing onlyPoolManager modifier",
        description="The hook functions must only be called by PoolManager.",
        impact="high"
    )
    return model


def model_misconfigured_hook() -> ThreatModelBase:
    def detect(scope: ContractScope, code: str = None) -> bool:
        _path = Loader().cache_content(code, "sol")
        return not is_valid_hook(_path)

    model = ThreatModelBase("contract")
    model.mount_rule(detect)
    model.override_metadata(
        summary="Misconfigured Hook",
        description="There are some hook functions that are not yet implemented, while the flags in getHookPermissions() are true.",
        impact="medium"
    )
    return model


def model_tx_origin() -> ThreatModelBase:
    def detect(scopes: list[FunctionScope], code: str = None) -> bool:
        for scope in scopes:
            for _cond in scope.access_control:
                if not _cond.logic:
                    continue
                if "tx.origin" in _cond.logic:
                    return True
        return False

    model = ThreatModelBase("function")
    model.mount_rule(detect)
    model.override_metadata(
        summary="Using tx.origin",
        description="Access Controlling using tx.orgin can be vulnerable at phishing.",
        impact="high"
    )
    return model


# before/after 내 사용 변수 중 mapping(키: PoolId)이 아닌 변수가 있는지 확인
# def model_double_initialize() -> ThreatModelBase:
#     def detect(scopes: list[FunctionScope], code: str = None) -> bool:
#         for scope in scopes:
#             for _cond in scope.access_control:
#                 if not _cond.logic:
#                     continue
#                 if "msg.sender" in _cond.logic:
#                     return True
#         return False
#
#     model = ThreatModelBase("function")
#     model.mount_rule(detect)
#     model.override_metadata(
#         summary="Double initialize",
#         description="There are some storage variables in the hook contract that are not stored as a mapping (PoolId=>), which can be dangerous if the hook is able to double-initialize.",
#         impact="high"
#     )
#     return model


# id = payable 함수/transfer 사용 함수일 경우, msg.sender에 대한 require문(balance check, contract owner check)가 있는지 확인해야 함
# def model_payable_function() -> ThreatModelBase:
#     def detect(scopes: list[FunctionScope], code: str = None) -> bool:
#         for scope in scopes:
#             # if function "payable"
#             # if body contains "transfer"
#             for _cond in scope.access_control:
#                 if not _cond.logic:
#                     continue
#                 if "msg.sender" in _cond.logic:
#                     return True
#         return False
#
#     model = ThreatModelBase("function")
#     model.mount_rule(detect)
#     model.override_metadata(
#         summary="Payable function",
#         description="There are some payable/transfer external function that does not check msg.sender is a proper caller.",
#         impact="medium"
#     )
#     return model
#


def get_model_suite():
    return [
        model_missing_token_transfer_while_burnt(),
        model_get_slot0_check(),
        model_low_call(),
        model_missing_only_pool_manager_modifier(),
        model_misconfigured_hook(),
        model_tx_origin()
    ]
