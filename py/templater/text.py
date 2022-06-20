import pprint

from py.readers.text import TextReader
from py.parsers.engine import EqualsExpression, TableExpression, IfExpression, TextExpression, UnlessExpression
from py.parsers.lexer import Lexer
from py.parsers.engine import Parser

class TextTemplateParser:
    def __init__(self, filename, context: dict):
        self.parser = Parser(Lexer(TextReader(filename)))
        self.context = context

    def parse(self):
        expressions = self.parser.parse()
        result = self.parse_expressions(expressions)
        return ''.join(result)

    def parse_expressions(self, expressions):
        result = []
        for expr in expressions:
            if not expr:
                continue
            result.extend(self.parse_token(expr))
        return result

    def parse_token(self, expr):
        if isinstance(expr, EqualsExpression):
            return str(eval(expr.token.val(), self.context))
        if isinstance(expr, TableExpression):
            return pprint.pformat(eval(expr.token.val(), self.context))
        if isinstance(expr, IfExpression):
            if eval(expr.condition.val(), self.context):
                return self.parse_expressions(expr.consequences)
            else:
                return ""
        if isinstance(expr, UnlessExpression):
            if not eval(expr.condition.val(), self.context):
                return self.parse_expressions(expr.consequences)
            else:
                return ""

        if isinstance(expr, TextExpression):
            return str(expr.text.val())

        print(expr, type(expr))
        raise SyntaxError('unparseable code')

