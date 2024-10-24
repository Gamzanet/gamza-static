class Logic:
    def __init__(self, native: str):
        self.native = native

    def __str__(self):
        return self.native

    def __repr__(self):
        return self.native

    def __eq__(self, other):
        return str(self) == str(other)

    def __or__(self, other: "Logic"):
        if self == "" or other == "":
            return Logic(f"{self}{other}")
        return Logic(f"({self} or {other})")

    def __and__(self, other: "Logic"):
        if self == "" or other == "":
            return Logic(f"{self}{other}")
        return Logic(f"({self} and {other})")

    def __invert__(self):
        if self == "" or self is None:
            return self
        return Logic(f"not({self})")


class LogicNode:
    def __init__(self, logic: "Logic", parent: "LogicNode" = None):
        self.logic = logic
        self._parent: LogicNode = self if parent is None else parent
        if parent is not None:
            print("parent", parent, "cur", self)
        self.children: list[LogicNode] = []

    @property
    def parent(self):
        return self._parent

    def __str__(self):
        return self.logic.__str__()

    @property
    def peers(self):
        return self.parent.children

    def concat_previous_children(self, condition: str) -> Logic:
        _children = self.children
        if len(_children) == 0:
            return Logic(condition)
        if condition:  # else if
            return Logic(condition) & ~_children[-1].logic
        return ~_children[-1].logic  # else


def add_child(parent: LogicNode, condition: str = None) -> LogicNode:
    child_node = LogicNode(
        parent.logic &
        parent.concat_previous_children(condition)
        , parent)
    parent.children.append(child_node)
    return child_node


_code_root_node = LogicNode(Logic(""), None)  # assume there is an empty root


def test_logic_operations():
    _logic_x = Logic("x > 0")
    _logic_y = Logic("y > 0")
    _logic_z = Logic("z > 0")
    assert _logic_x == "x > 0"
    assert ~_logic_x == "not(x > 0)"
    assert _logic_x | _logic_y == "(x > 0 or y > 0)"
    assert _logic_x & _logic_y == "(x > 0 and y > 0)"
    assert _logic_x | _logic_y | _logic_z == "((x > 0 or y > 0) or z > 0)"
    assert _logic_x & _logic_y & _logic_z == "((x > 0 and y > 0) and z > 0)"


def test_layer1_else_if():
    _given = "if (x > 0) {} else if (y > 0) {}"
    _expect = ["x > 0", "y > 0"]
    root = LogicNode(Logic(""), None)  # to start from empty root
    n0 = add_child(root, _expect[0])  # add first child
    n1 = add_child(root, _expect[1])  # add second child in the same level
    assert n0.logic == "x > 0"
    assert n1.logic == "(y > 0 and not(x > 0))"


def test_layer1_else():
    _given = "if (x > 0) {} else if (y > 0) {} else {}"
    _expect = ["x > 0", "y > 0"]
    root = LogicNode(Logic(""), None)  # start from empty root
    n0 = add_child(root, _expect[0])  # add first if
    n1 = add_child(root, _expect[1])  # add second else-if in the same level
    n2 = add_child(root)  # add third else in the same level
    assert n0.logic == "x > 0"
    assert n1.logic == "(y > 0 and not(x > 0))"
    assert n2.logic == "not((y > 0 and not(x > 0)))"


def test_layer2_if():
    _given = "if (x > 0) { if (y > 0) {} }"
    _expect = ["x > 0", ["y > 0"]]
    root = LogicNode(Logic(""), None)  # start from empty root
    n0 = add_child(root, _expect[0])  # add first if
    n1 = add_child(n0, _expect[1][0])  # add second if in the first if
    assert str(n0) == "x > 0"
    assert str(n1) == "(x > 0 and y > 0)"


def test_layer2_else_if():
    _given = "if (x > 0) { if (y > 0) {} else if (z > 0) {} }"
    _expect = ["x > 0", ["y > 0", "z > 0"]]
    root = LogicNode(Logic(""), None)  # start from empty root
    n0 = add_child(root, _expect[0])  # add first if
    n1 = add_child(n0, _expect[1][0])  # add second if in the first if
    n2 = add_child(n0, _expect[1][1])  # add second else-if in the first if
    assert str(n0) == "x > 0"
    assert str(n1) == "(x > 0 and y > 0)"
    assert str(n2) == "(x > 0 and (z > 0 and not((x > 0 and y > 0))))"
