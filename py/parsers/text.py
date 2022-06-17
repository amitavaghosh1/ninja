from enum import Enum
from collections import namedtuple

PERCENTAGE = "%"
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

class Reader:
    def __init__(self, string):
        self.string = string
        self.strlen = len(string)
        self.index = 0

    def read(self):
        if self.strlen <= self.index:
            return None

        c = self.string[self.index]
        self.index += 1
        return c

    def read_n(self, n: int):
        if self.strlen <= self.index:
            return None

        c = self.string[0:n]
        self.index += n
        return c

    def peek(self):
        if self.strlen < self.index:
            return None
        return self.string[self.index]


    def peek_n(self, n):
        return self.string[self.index:self.index+n]

    def eof(self):
        return self.index >= self.strlen


class TokenizeTextTemplate:
    def __init__(self, reader):
        self.chars = []
        self.reader = reader

    def read(self):
        c = self.reader.read()
        self.chars.append(c)

        tokens_so_far = ''.join(self.chars)

        if tokens_so_far in TEMPLATE_SYNTAXES:
            self.chars = []
            return tokens_so_far

        print("x", self.reader.peek_n(2))
        if self.reader.peek_n(2) == TEMPLATE_END:
            self.chars = []
            return tokens_so_far

        if c == PERCENTAGE and self.reader.peek() == '}':
            self.chars = []
            return tokens_so_far + self.reader.read()

        return None

    def rest(self):
        if len(self.chars) > 0:
            return ''.join(self.chars)
        return None

class ParseTextTemplate:
    def __init__(self):
        self.state = States.IDLE
        self.tokens = []
        self.ifstart = ""

    def __reset_tokens__(self):
        self.tokens = []

    def __reset_state__(self):
        self.state = States.IDLE

    def __reset__(self):
        self.__reset_tokens__()
        self.__reset_state__()

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

        # print("token =>",  token, self.state)

        match self.state:
            case States.READING_IF:
                self.tokens.append(token)

                if token == TEMPLATE_END:
                    self.ifstart = ''.join(self.tokens).strip()
                    self.__reset_tokens__()
                    return Token("if", self.ifstart)

            case States.READING_END:
                self.tokens.append(token)

                if token == TEMPLATE_END:
                    endtag = ''.join(self.tokens).strip()
                    if endtag != self.ifstart:
                        raise Exception("%s if block mismatch" % self.ifstart)
                    self.__reset__()
                    # self.state = States.IDLE # this should be recursive to support nested if
                    return Token("end", self.ifstart)

            case States.READING_VAR:
                self.tokens.append(token)

                if token == TEMPLATE_END:
                    t = ''.join(self.tokens)
                    self.__reset__()
                    return Token("var", t)

            case States.READING_TABLE:
                self.tokens.append(token)

                if token == TEMPLATE_END:
                    t = ''.join(self.tokens)
                    self.__reset__()
                    return Token("table", t)

            case _:
                pass

        # self.state = States.IDLE
        return None

    # def read_if(self, token):
        # pass

    # def read_var(self):
        # pass

    # def read_string(self):
        # pass


def read(string):
    r = Reader(string)
    t = TokenizeTextTemplate(r)
    p = ParseTextTemplate()

    data = ''
    while not r.eof():
        data = t.read()
        if data is None:
            continue

        token = p.read_token(data)
        if token is None:
            continue

        print(token)

    # data = t.rest()
    # if data is None:
        # return

    # token = p.read_token(data)
    # if token is not None:
        # print(token)

