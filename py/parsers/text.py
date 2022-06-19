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


class ArrayBuffer:
    def __init__(self):
        self.buf = []

    def append(self, v):
        self.buf.append(v)

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

    def __str__(self):
        return "EXPR: %s" % self.val()

class ExpressionTypeToken:
    SymbolMap = {
        Symbol.AT: "table",
        Symbol.EQUALS: "equals",
        Symbol.HASH: "if",
        Symbol.SLASH: "end",
    }

    def __init__(self, symbol):
        self.symbol = symbol

    def val(self) -> str:
        return ExpressionTypeToken.SymbolMap[self.symbol]

    def __str__(self):
        return "EXPR_TYPE: %s" % ExpressionTypeToken.SymbolMap[self.symbol]


class Lexer:
    def __init__(self, reader: Reader):
        self.reader = reader
        self.state = LexerStates.IDLE
        self.buffer = ArrayBuffer()

    def eof(self):
        return self.reader.eof()

    def peek(self):
        pass

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


class ParserStates:
    IDLE = None

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.state = ParserStates.IDLE

    def parse(self):
        token = self.lexer.read()

        if isinstance(token, EOF):
            return "something"

        while token:
            if isinstance(token, ExpressionTypeToken):
                self.parse_expression()
            if isinstance(token, TextToken):
                self.parse_text()

    def parse_expression(self):
        pass

    def parse_text(self):
        pass



class TexTemplateParser:
    def __init__(self, parser):
        self.parser = parser
