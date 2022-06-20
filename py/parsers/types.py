class Symbol:
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    PERCENTAGE = "%"
    EQUALS = "="
    HASH = "#"
    AT = "@"
    SLASH = "/"
    NOT = "^"
    ALL = [LEFT_BRACE, RIGHT_BRACE, PERCENTAGE, EQUALS, AT, HASH, SLASH, NOT]


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
    Unless = "unless"

class EOF:
    def __init__(self, token) -> None:
        self.token = token

    def val(self):
        return self.token

    def __str__(self) -> str:
        return "EOF" if self.token is None else str(self.token)

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
        Symbol.NOT: ExpressionTokens.Unless,
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

