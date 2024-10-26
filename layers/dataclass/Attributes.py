import enum


class Purity(enum.Enum):
    PURE = "pure"
    VIEW = "view"

    @staticmethod
    def from_str(value: str):
        if value is None:
            return None
        mapping = {
            "pure": Purity.PURE,
            "view": Purity.VIEW
        }
        return mapping.get(value.lower())



class Visibility(enum.Enum):
    PUBLIC = "public"
    EXTERNAL = "external"
    INTERNAL = "internal"
    PRIVATE = "private"

    @staticmethod
    def from_str(value: str):
        if value is None:
            return None
        mapping = {
            "public": Visibility.PUBLIC,
            "external": Visibility.EXTERNAL,
            "internal": Visibility.INTERNAL,
            "private": Visibility.PRIVATE
        }
        return mapping.get(value.lower())


class Mutability(enum.Enum):
    MUTABLE = "mutable"
    IMMUTABLE = "immutable"
    CONSTANT = "constant"
    TRANSIENT = "transient"

    @staticmethod
    def from_str(value: str):
        if value is None:
            return None
        mapping = {
            "mutable": Mutability.MUTABLE,
            "immutable": Mutability.IMMUTABLE,
            "constant": Mutability.CONSTANT,
            "transient": Mutability.TRANSIENT
        }
        return mapping.get(value.lower())


class Scope(enum.Enum):
    FUNCTION = "function"
    STORAGE = "storage"
    ARGS = "args"
    RETURNS = "returns"
    INHERITED = "inherited"  # TODO: classify 'INHERITED'

    @staticmethod
    def from_str(value: str):
        if value is None:
            return None
        mapping = {
            "function": Scope.FUNCTION,
            "storage": Scope.STORAGE,
            "args": Scope.ARGS,
            "returns": Scope.RETURNS,
            "inherited": Scope.INHERITED
        }
        return mapping.get(value.lower())


class Location(enum.Enum):
    CALLDATA = "calldata"
    MEMORY = "memory"
    STORAGE = "storage"
    TRANSIENT = "transient"  # TODO: classify 'TRANSIENT'

    @staticmethod
    def from_str(value: str):
        if value is None:
            return None
        mapping = {
            "calldata": Location.CALLDATA,
            "memory": Location.MEMORY,
            "storage": Location.STORAGE,
            "transient": Location.TRANSIENT
        }
        return mapping.get(value.lower())
