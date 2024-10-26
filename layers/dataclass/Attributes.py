import enum


class Visibility(enum.Enum):
    PUBLIC = 1
    EXTERNAL = 2
    INTERNAL = 3
    PRIVATE = 4


class Mutability(enum.Enum):
    MUTABLE = 1
    IMMUTABLE = 2
    CONSTANT = 3
    TRANSIENT = 4


class Scope(enum.Enum):
    FUNCTION = 1
    STORAGE = 2
    ARGS = 3
    RETURNS = 4
    INHERITED = 5  # TODO: classify 'INHERITED'


class Location(enum.Enum):
    CALLDATA = 1
    MEMORY = 2
    STORAGE = 3
    TRANSIENT = 4  # TODO: classify 'TRANSIENT'
