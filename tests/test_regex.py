import re

from tests.test_eval import Logic, LogicNode, add_child


def test_parse_if_else():
    print()
    _given = """
        {
            if (x > 0) {
                if (y > 0) {
                // do nothing
                }
            }
        }
        if (x > 0) {
            revert();
            for (int i = 0; i < 10; i++) {
                if (i == 0) {
                    revert();
                } else if (i == 1) {
                    assert(y > 0);
                }
            }        
        x > 0;
        if (y > 0) {
            revert();
        } else if (z > 0) {
            assert(y > 0);
        } else {
            require(y > 0 or z > 0);
        }
    }
    """
    # _given = open("code/1.sol", "r").read()

    _given = (_given
              .replace("{", "\n{")
              .replace("}", "}\n")
              .replace("(", "\n(")
              .replace(")", ")\n")).splitlines()
    _given = list(map(str.strip, _given))
    for line in _given:
        print(line)
    print()
    stack = ConditionStack()
    for line in _given:
        if line:
            stack_dump = stack.__str__()
            stack.push(line)
            if stack_dump != stack.__str__():
                print(stack)


class ConditionStack:
    def __init__(self):
        self.cur = LogicNode(Logic(""), None)
        self.stack = []
        self.keywords = ["if", "else", "else if", "require", "assert", "revert"]
        self.leaf_keywords = ["require", "assert", "revert"]

    def reset(self):
        self.cur = LogicNode(Logic(""), None)
        self.stack = []

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
        if item == "{" and not self.is_condition(self.peek()):
            return False
        if item == "}" and self.is_empty():
            return False
        if "else" in item and len(self.cur.peers) == 0:
            return False
        return True

    def push(self, item):
        if not self.is_valid(item):
            return
        if self.is_condition(item) and self.peek() in self.keywords:
            assert self.peek() != "else"  # else already filtered
            _unwrapped = item[1:-1]
            if self.peek() in self.leaf_keywords:
                # print(self.cur.parent.logic)
                print(f"{self.pop()}:{self.cur.logic & Logic(_unwrapped)}")
                return
            if self.cur.parent is None:
                self.cur = add_child(self.cur, _unwrapped)

            self.cur = add_child(self.cur, _unwrapped)

        #
        # if self.is_condition(item) and self.peek in self.leaf_keywords:
        #     print("leaf", item,)
        #     return
        # if self.is_condition(item) and self.peek() == "if":
        #     self.cur =  add_child(self.cur, item)
        # if item == "{":
        #     self.cur = add_child(self.cur, self.peek()[1:-1])
        #     # print(self.cur)

        # if self.peek() == "if":
        # # new node will be a child of the current node
        #
        # else:
        #     # new node will be a peer of the current node
        #     self.cur = add_child(self.cur.parent, _unwrapped)

        # finish current depth
        if item == "}":
            self.cur = self.cur.parent
            # print(self.cur)
            while True:
                self.pop()
                if self.is_empty():
                    self.reset()
                    return
                elif self.peek() == "{":
                    return
        self.stack.append(item)

        # if item == "if":
        #     self.stack.append(self.cur)
        # if re.match(r"\(.+\)", item):
        # self.cur = add_child(self.cur, item)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def is_empty(self):
        return len(self.stack) == 0

    def __str__(self):
        return str(self.stack)
