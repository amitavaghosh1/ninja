from sys import dont_write_bytecode
from typing import Text
from py.readers.reader import Reader
from copy import deepcopy
# from dataclasses import dataclass

# {%= time.strftime("%Y-%m-%d", time.localtime()) %}
#  Examples
## Text
### States: [IDLE, READING_NORMAL_TEXT]
### TEXT = "Text"

## {%= value %}
### States: [
####### (IDLE, READING_LEFT_BRACE)
####### (READING_LEFT_BRACE, READING_SYMBOL)
####### (READING_SYMBOL, READING_EXPRESSION)
####### (READING_EXPRESSION, IDLE)]
### EXPRESSION_TYPE = "="
### EXPRESSION = "value"

## Text {%= value %}
### States: [
####### (IDLE, READING_NORMAL_TEXT),
####### (READING_NORMAL_TEXT, READING_LEFT_BRACE),
####### (READING_LEFT_BRACE, READING_SYMBOL),
####### (READING_SYMBOL, READING_EXPRESSION),
####### (READING_EXPRESSION, IDLE)]
### TEXT = "Text "
### EXPRESSION_TYPE = "equals"
### EXPRESSION = "value"

## {%# hasEmail %} Email {%/ hasEmail %}
### States: [
####### (IDLE, READING_LEFT_BRACE),
####### (READING_LEFT_BRACE, READING_SYMBOL),
####### (READING_SYMBOL, READING_EXPRESSION)
####### (READING_EXPRESSION, IDLE),
####### (IDLE, READING_NORMAL_TEXT),
####### (READING_NORMAL_TEXT, READING_LEFT_BRACE)
#######]


#### we are using state_machine for lexing
# starts with None state
# state transitions:
### IDLE => READING_LEFT_BRACE
### IDLE => READING_NORMAL_TEXT

### READING_LEFT_BRACE => READING_SYMBOL
### READING_LEFT_BRACE => READING_NORMAL_TEXT

### READING_SYMBOL => READING_EXPRESSION (and Emit)
### READING_SYMBOL => INVALID_SYNTAX

### READING_EXPRESSION => IDLE (and Emit)

### READING_NORMAL_TEXT => IDLE (and Emit)
### READING_NORMAL_TEXT => READING_LEFT_BRACE

### Implicit State => EOF
### Return Expression or ExpressionType depending on state

class Symbol:
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    PERCENTAGE = "%"
    EQUALS = "="
    HASH = "#"
    AT = "@"
    SLASH = "/"
    ALL = [LEFT_BRACE, RIGHT_BRACE, PERCENTAGE, EQUALS, AT, HASH, SLASH]


class LexerStates:
    IDLE = None
    READING_LEFT_BRACE = "READING_LEFT_BRACE"
    READING_SYMBOL = "READING_SYMBOL"
    READING_NORMAL_TEXT = "READING_NORMAL_TEXT"
    READING_EXPRESSION = "READING_EXPRESSION"


class ExpressionTokens:
    Equals = "equals"
    Table = "table"
    If = "if"
    End = "end"

class ArrayBuffer:
    def __init__(self):
        self.buf = []

    def append(self, v):
        self.buf.append(v)

    def pop(self):
        return self.buf.pop()

    def drain(self):
        result = deepcopy(self.buf)
        self.buf = []
        return result

    def __str__(self):
        return "[ %s ]" % ', '.join(self.buf)



class EOF:
    def __init__(self, token) -> None:
        self.token = token

    def __str__(self) -> str:
        return self.token

class TextToken:
    def __init__(self, buffer) -> None:
        self.buffer = buffer

    def val(self) -> str:
        return ''.join(self.buffer)

    def __str__(self) -> str:
        return "TEXT: %s" % ''.join(self.buffer)

class ExpressionToken:
    def __init__(self, buffer) -> None:
        self.buffer = buffer

    def val(self):
        return ''.join(self.buffer)

    def __eq__(self, obj):
        return obj.val() == self.val()

    def __str__(self):
        return "EXPR: %s" % self.val()

class ExpressionTypeToken:
    SymbolMap = {
        Symbol.AT: ExpressionTokens.Table,
        Symbol.EQUALS: ExpressionTokens.Equals,
        Symbol.HASH: ExpressionTokens.If,
        Symbol.SLASH: ExpressionTokens.End,
    }

    __ReverseMap__ = {
        ExpressionTokens.Table: Symbol.AT,
        ExpressionTokens.Equals: Symbol.EQUALS,
        ExpressionTokens.If: Symbol.HASH,
        ExpressionTokens.End: Symbol.SLASH,
    }

    def __init__(self, symbol):
        self.symbol = symbol

    def val(self) -> str:
        return ExpressionTypeToken.SymbolMap[self.symbol]

    def __eq__(self, key) -> bool:
        does_symbols_match = ExpressionTypeToken.SymbolMap[self.symbol] == key
        return isinstance(key, str) and does_symbols_match

    def __str__(self):
        return "EXPR_TYPE: %s" % ExpressionTypeToken.SymbolMap[self.symbol]


class Lexer:
    def __init__(self, reader: Reader):
        self.reader = reader
        self.state = LexerStates.IDLE
        self.buffer = ArrayBuffer()
        self.peeked_token = None

    def eof(self):
        return self.reader.eof()

    def peek(self):
        if self.peeked_token:
            return self.peeked_token

        token = self.read_token()
        self.peeked_token = token
        return token

    def next(self):
        if self.peeked_token:
            peeked_token = self.peeked_token
            self.peeked_token = None
            return peeked_token

        return self.read_token()

    def read_token(self):
        if self.eof():
            return None

        while True:
            token = self.read()
            if not token:
                continue
            if isinstance(token, EOF):
                return None
            return token

    def read(self):
        if self.reader.eof():
            if self.state == LexerStates.READING_NORMAL_TEXT:
                return EOF(TextToken(self.buffer.drain()))
            if self.state == LexerStates.READING_EXPRESSION:
                return EOF(ExpressionToken(self.buffer.drain()))
            return EOF(None)

        character = self.reader.read()

        match self.state:
            case None:
                if character == Symbol.LEFT_BRACE:
                    self.state = LexerStates.READING_LEFT_BRACE
                else:
                    self.state = LexerStates.READING_NORMAL_TEXT
            case LexerStates.READING_LEFT_BRACE:
                if character == Symbol.PERCENTAGE:
                    self.state = LexerStates.READING_SYMBOL
                else:
                    self.state = LexerStates.READING_NORMAL_TEXT
                    self.buffer.append(Symbol.LEFT_BRACE)
            case LexerStates.READING_NORMAL_TEXT:
                if character == Symbol.LEFT_BRACE:
                    self.state = LexerStates.READING_LEFT_BRACE
                    return TextToken(self.buffer.drain())
                else:
                    self.buffer.append(character)
            case LexerStates.READING_SYMBOL:
                if character in Symbol.ALL:
                    self.state = LexerStates.READING_EXPRESSION
                    return ExpressionTypeToken(character)
                else:
                    raise SyntaxError("INVALID_SYNTAX %s" % character)
            case LexerStates.READING_EXPRESSION:
                if character == Symbol.PERCENTAGE:
                    assert self.reader.peek() == Symbol.RIGHT_BRACE, 'SyntaxError: invalid_syntax'
                    self.state = LexerStates.IDLE  # end of parsing expression
                    return ExpressionToken(self.buffer.drain())
                else:
                    self.buffer.append(character)
            case _:
                pass


## EXPR_TYPE: equals
## EXPR:  date
## TEXT:
##
## Hi,
## EXPR_TYPE: equals
## EXPR:  user.fullname
## TEXT: .
##
##
## EXPR_TYPE: if
## EXPR:  hasEmail
## TEXT:
##
## EXPR_TYPE: if
## EXPR:  isGoogleEmail
## TEXT: You have a
##     gmail email
##
## EXPR_TYPE: end
## EXPR:  isGoogleEmail
## TEXT:
##
## EXPR_TYPE: end
## EXPR:  hasEmail
## TEXT:
##
##
## EXPR_TYPE: table
## EXPR:  table_data

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def parse(self):
        buffer = []

        while True:
            token = self.lexer.peek()
            # print("token ", token)

            if not token:
                return buffer

            if isinstance(token, EOF):
                return buffer

            if isinstance(token, ExpressionTypeToken):
                if token == ExpressionTokens.End:
                    return buffer
                self.lexer.next()
                expr = self.parse_expression(token)
                buffer.append(expr)
            elif isinstance(token, TextToken):
                self.lexer.next()
                buffer.append(token)
            else:
                raise SyntaxError('invalid token')

    def parse_expression(self, token):
        # print("parsing token expression ", token, type(token))

        if token == ExpressionTokens.Equals:
            return self.parse_expression_equals()
        elif token == ExpressionTokens.Table:
            return self.parse_expression_table()
        elif token == ExpressionTokens.If:
            return self.parse_expression_if()
        else:
            raise SyntaxError('invalid syntax for expression')

    def parse_expression_equals(self):
        v = self.lexer.next()
        assert isinstance(v, ExpressionToken), v

        return { "type": ExpressionTokens.Equals, "var": v }

    def parse_expression_table(self):
        v = self.lexer.next()
        assert isinstance(v, ExpressionToken), v

        return { "type": ExpressionTokens.Table, "var": v }

    def parse_expression_if(self):
        condition = self.lexer.next()
        assert isinstance(condition, ExpressionToken), 'invalid token %s' % condition

        consequences = self.parse()

        end = self.lexer.next()
        assert isinstance(end, ExpressionTypeToken) and end == ExpressionTokens.End, 'if missing end'

        endexpr = self.lexer.next()
        assert isinstance(endexpr, ExpressionToken) and endexpr == condition, 'if closed unexpectedly'
        return { "type": "if", "condition": condition, "consequences": consequences }


class TextTemplateParser:
    def __init__(self, filename):
        self.parser = Parser(Lexer(filename))

    def parse(self):
        tokens = self.parser.parse()
