import re
from threading import Condition

from attr import dataclass


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
        return Logic(f"(({self}) or ({other}))")

    def __and__(self, other: "Logic"):
        if self == "" or other == "":
            return Logic(f"{self}{other}")
        return Logic(f"(({self}) and ({other}))")

    def __invert__(self):
        if self == "" or self is None:
            return self
        return Logic(f"not({self})")


class LogicNode:
    def __init__(self, logic: "Logic", parent: "LogicNode" = None):
        self.logic = logic
        self._parent: LogicNode = self if parent is None else parent
        # if parent is not None:
        #     print("parent", parent, "cur", self)
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


def add_child(parent: LogicNode, condition: str = "") -> LogicNode:
    child_node = LogicNode(
        parent.logic &
        parent.concat_previous_children(condition)
        , parent)
    # print("child", child_node)
    parent.children.append(child_node)
    return child_node


class Tokenizer:
    def __init__(self, code: str):
        self.code = self.tokenize(code)

    @staticmethod
    def tokenize(code: str) -> list[str]:
        # remove comments
        code = re.sub(r"//[\S ]+", "", code)

        # all kinds of spaces to single space
        code = re.sub(r"\s+", " ", code)

        # TODO: <temp> focus on contract scope
        code = re.search(r"contract\s+[\s\S]+}", code).group(0)

        # tokenize
        code = (
            code
            .replace("else if", "$elf$")
            .replace("if", "$if$")
            .replace("else", "$els$")
            .replace("require", "$req$")
            .replace("assert", "$asrt$")
            .replace("revert()", "$revX$")
            .replace("revert", "$rev$")
        )

        pattern = r"\$\w+\$\s*\([\s\S]+?\)\;|[\{\}]|\$\w+\$"
        code = "\n".join(re.findall(pattern, code))
        code = re.sub(r"\$rev\$[\s\S]+?;", "$revX$;", code)
        code = re.sub(r",\s*\"[\w ]+\"", "", code)

        code = (
            code
            .replace(";", "")
            .replace("$req$", "\nrequire\n")
            .replace("$asrt$", "\nassert\n")
            .replace("$rev$", "\nrevert\n")
            .replace("$revX$", "\nrevert\n()\n")
            .replace("$if$", "\nif\n")
            .replace("$els$", "\nelse\n")
            .replace("$elf$", "\nelse if\n")
            .replace("{", "\n{\n")
            .replace("}", "}\n")
            .replace(";", " ")
        )

        code = code.splitlines()
        code = list(map(str.strip, code))

        return code


@dataclass
class Condition:
    method: str
    logic: Logic

    def __str__(self):
        return f"{self.method}:{self.logic.native}"


class ConditionStack:
    def __init__(self):
        self.cur = LogicNode(Logic(""), None)
        self.stack = []
        self.keywords = ["if", "else", "else if", "require", "assert", "revert"]
        self.leaf_keywords = ["require", "assert", "revert"]
        self.conditions: list[Condition] = []

    @staticmethod
    def is_condition(item):
        return re.match(r"\([\s\S]*\)", item)

    def is_valid(self, item) -> bool:
        if not (self.is_condition(item) or item in self.keywords or item in ["{", "}"]):
            return False
        if self.is_empty() and item not in self.keywords:
            return False
        if self.is_condition(item) and self.peek() not in self.keywords:
            return False
        if self.is_condition(item) and self.peek() in ["else"]:
            return False
        if item == "{":
            if not self.is_condition(self.peek()) and self.peek() != "else":
                return False
        if item == "}" and (self.is_empty() or self.peek() != "{"):
            return False
        if "else" in item and len(self.cur.peers) == 0:
            return False
        return True

    def push(self, item):
        if not self.is_valid(item):
            return

        if self.is_empty():
            self.stack.append(item)
            if self.peek() == "if":
                self.cur = LogicNode(Logic(""), None)
            return

        if self.is_condition(item) and self.peek() in self.leaf_keywords:
            _unwrapped = item[1:-1]
            self.conditions.append(Condition(self.pop(), Logic(self.cur.logic & Logic(_unwrapped))))
            return

        # TODO: currently, if-else block should use brackets

        if item == "}":
            assert self.pop() == "{"
            while not self.is_empty():
                _tmp = self.pop()
                if _tmp == "{":
                    self.stack.append(_tmp)
                    break
            self.cur = self.cur.parent
            return

        if item == "{":
            if self.peek() == "else":
                self.cur = add_child(self.cur.parent, "")
                self.stack.append(item)
                return

            _cond = self.pop()
            _key = self.peek()
            self.stack.append(_cond)
            self.cur = add_child(self.cur, _cond)

        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def is_empty(self):
        return len(self.stack) == 0

    def __str__(self):
        return str(self.stack)
