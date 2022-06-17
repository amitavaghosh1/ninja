from enum import Enum
from collections import namedtuple


TEMPLATE_END = "%}"
TEMPLATE_VAR_BLOCK = "{%="
TEMPLATE_IF_BLOCK = "{%#"
TEMPLATE_END_BLOCK = "{%/"
TEMPLATE_TABLE_BLOCK = "{%@"

TEMPLATE_SYNTAXES = [TEMPLATE_VAR_BLOCK, TEMPLATE_IF_BLOCK, TEMPLATE_END_BLOCK, TEMPLATE_TABLE_BLOCK]

class States(Enum):
    IDLE = 1
    READING_IF = 2
    READING_VAR = 3

class TokenTypes(Enum):
    VAR = 1
    IF = 2
    TABLE = 3
    TEXT = 4

Token = namedtuple("Token", "tok_type data")

class TokenizeTextTemplate:
    def __init__(self):
        self.chars = []

    def read(self, c):
        self.chars.append(c)

        token_so_far = ''.join(self.chars)
        if token_so_far in TEMPLATE_SYNTAXES:
            self.chars = []
            return token_so_far
        return None


class ParseTextTemplate:
    def __init__(self):
        self.state = States.IDLE

    def read_token(self, token):
        if self.state == States.IDLE:
            if token == TEMPLATE_IF_BLOCK:
                self.state = States.READING_IF
            elif token in [TEMPLATE_VAR_BLOCK, TEMPLATE_TABLE_BLOCK]:
                self.state = States.READING_VAR
            else:
                pass

        match self.state:
            case States.READING_IF:
                pass
            case States.READING_VAR:
                pass
            case _:
                pass

        self.state = States.IDLE
        return None


def read(string):
    t = TokenizeTextTemplate()
    p = ParseTextTemplate()

    for c in string:
        data = t.read(c)
        if data is None:
            continue

        token = p.read_token(data)
        if token is None:
            raise Exception("broke!!")



