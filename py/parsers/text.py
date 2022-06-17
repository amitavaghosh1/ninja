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
    READING_VAR = 2
    READING_IF = 3
    READING_END = 4
    READING_TABLE = 5

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
        self.tokens = []
        self.ifstart = ""

    def __reset_tokens(self):
        self.tokens = []

    def read_token(self, token):
        if self.state == States.IDLE:
            if token == TEMPLATE_IF_BLOCK:
                self.state = States.READING_IF
            if token == TEMPLATE_END_BLOCK:
                self.state = States.READING_END
            elif token == TEMPLATE_VAR_BLOCK:
                self.state = States.READING_VAR
            elif token == TEMPLATE_TABLE_BLOCK:
                self.state = States.READING_TABLE
            else:
                pass

        match self.state:
            case States.READING_IF:
                if token == '}':
                    self.ifstart = ''.join(self.tokens).strip()
                    self.__reset_tokens()
                    return Token("if", self.ifstart)

                self.tokens.append(token)
            case States.READING_END:
                if token == '}':
                    endtag = ''.join(self.tokens).strip()
                    if endtag != self.ifstart:
                        raise Exception("%s if block mismatch" % self.ifstart)
                    self.__reset_tokens()
                    self.state = States.IDLE # this should be recursive to support nested if
                    return Token("end", self.ifstart)

                self.tokens.append(token)
            case States.READING_VAR:
                if token == '}':
                    t = ''.join(self.tokens)
                    self.__reset_tokens()
                    return Token("var", t)

                self.tokens.append(token)
            case States.READING_TABLE:
                if token == '}':
                    t = ''.join(self.tokens)
                    self.__reset_tokens()
                    return Token("table", t)

                self.tokens.append(token)
            case _:
                pass

        self.state = States.IDLE
        return None

    # def read_if(self, token):
        # pass

    # def read_var(self):
        # pass

    # def read_string(self):
        # pass


class Reader:
    def __init__(self, string):
        self.string = string
        self.index = 0

    def read(self):
        if len(self.string) <= self.index:
            return None

        c = self.string[self.index]
        self.index += 1
        return c

    def read_n(self, n: int):
        if len(self.string) <= self.index:
            return None

        c = self.string[0:n]
        self.index += n
        return c



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


