import attr


@attr.frozen(auto_attribs=True)
class Type:
    value: str

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other or self == other


@attr.frozen(auto_attribs=True)
class Purity(Type):
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


@attr.frozen(auto_attribs=True)
class Visibility(Type):
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


@attr.frozen(auto_attribs=True)
class Mutability(Type):
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


@attr.s(auto_attribs=True)
class Scope(Type):
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


@attr.s(auto_attribs=True)
class Location(Type):
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


@attr.frozen(auto_attribs=True)
class Condition:
    method: str
    logic: str
