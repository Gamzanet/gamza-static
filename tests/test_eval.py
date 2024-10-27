from engine.lexer import Logic, LogicNode, add_child


def test_logic_operations():
    _logic_x = Logic("x > 0")
    _logic_y = Logic("y > 0")
    _logic_z = Logic("z > 0")
    assert _logic_x == "x > 0"
    assert ~_logic_x == "not(x > 0)"
    assert _logic_x | _logic_y == "((x > 0) or (y > 0))"
    assert _logic_x & _logic_y == "((x > 0) and (y > 0))"
    assert _logic_x | _logic_y | _logic_z == "((((x > 0) or (y > 0))) or (z > 0))"
    assert _logic_x & _logic_y & _logic_z == "((((x > 0) and (y > 0))) and (z > 0))"


def test_layer1_else_if():
    _given = "if (x > 0) {} else if (y > 0) {}"
    _expect = ["x > 0", "y > 0"]
    root = LogicNode(Logic(""), None)  # to start from empty root
    n0 = add_child(root, _expect[0])  # add first child
    n1 = add_child(root, _expect[1])  # add second child in the same level
    assert n0.logic == "x > 0"
    assert n1.logic == "((y > 0) and (not(x > 0)))"


def test_layer1_else():
    _given = "if (x > 0) {} else if (y > 0) {} else {}"
    _expect = ["x > 0", "y > 0"]
    root = LogicNode(Logic(""), None)  # start from empty root
    n0 = add_child(root, _expect[0])  # add first if
    n1 = add_child(root, _expect[1])  # add second else-if in the same level
    n2 = add_child(root)  # add third else in the same level
    assert n0.logic == "x > 0"
    assert n1.logic == "((y > 0) and (not(x > 0)))"
    assert n2.logic == "not(((y > 0) and (not(x > 0))))"


def test_layer2_if():
    _given = "if (x > 0) { if (y > 0) {} }"
    _expect = ["x > 0", ["y > 0"]]
    root = LogicNode(Logic(""), None)  # start from empty root
    n0 = add_child(root, _expect[0])  # add first if
    n1 = add_child(n0, _expect[1][0])  # add second if in the first if
    assert str(n0) == "x > 0"
    assert str(n1) == "((x > 0) and (y > 0))"


def test_layer2_else_if():
    _given = "if (x > 0) { if (y > 0) {} else if (z > 0) {} }"
    _expect = ["x > 0", ["y > 0", "z > 0"]]
    root = LogicNode(Logic(""), None)  # start from empty root
    n0 = add_child(root, _expect[0])  # add first if
    n1 = add_child(n0, _expect[1][0])  # add second if in the first if
    n2 = add_child(n0, _expect[1][1])  # add second else-if in the first if
    assert str(n0) == "x > 0"
    assert str(n1) == "((x > 0) and (y > 0))"
    assert str(n2) == "((x > 0) and (((z > 0) and (not(((x > 0) and (y > 0)))))))"
