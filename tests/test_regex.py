import re

from tests.test_eval import Logic, LogicNode, add_child


def test_parse_if_else():
    print()
    _given = open("code/1.sol", "r").read()

    # TODO: <temp> focus on contract scope
    _given = re.search(r"contract\s+[\s\S]+}", _given).group(0)

    # remove comments
    _given = re.sub(r"//[\S ]+", "", _given)

    # # remove library
    # _given = re.sub(r"using\s+[\s\S]+?;", "", _given)

    # all kinds of spaces to single space
    _given = re.sub(r"\s+", " ", _given)

    # tokenize
    _given = (
        _given
        .replace("else if", "$elf$")
        .replace("if", "$if$")
        .replace("else", "$els$")
        .replace("require", "$req$")
        .replace("assert", "$asrt$")
        .replace("revert()", "$revX$")
        .replace("revert", "$rev$")
    )

    pattern = r"\$\w+\$\s*\([\s\S]+?\)\;|[\{\}]|\$\w+\$"
    _given = "\n".join(re.findall(pattern, _given))
    _given = re.sub(r"\$rev\$[\s\S]+?;", "$revX$;", _given)
    _given = re.sub(r",\s*\"[\w ]+\"", "", _given)

    # print(_given)

    _given = (
        _given
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

    _given = _given.splitlines()
    _given = list(map(str.strip, _given))

    stack = ConditionStack()
    for line in _given:
        if line != "":
            # print(line)
            stack_dump = stack.__str__()
            stack.push(line.strip())
            if stack_dump != stack.__str__():
                # print(stack)
                pass


class ConditionStack:
    def __init__(self):
        self.cur = LogicNode(Logic(""), None)
        self.stack = []
        self.keywords = ["if", "else", "else if", "require", "assert", "revert"]
        self.leaf_keywords = ["require", "assert", "revert"]

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
            print(f"{self.pop()}:{self.cur.logic & Logic(_unwrapped)}")
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
