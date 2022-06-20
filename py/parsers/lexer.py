from py.readers.reader import Reader
from py.parsers.buffer import ArrayBuffer
from py.parsers.types import Symbol, LexerStates
from py.parsers.types import EOF, ExpressionToken, TextToken, ExpressionTypeToken

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



