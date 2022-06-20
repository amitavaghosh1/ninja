from py.parsers.types import ExpressionTokens
from py.parsers.types import EOF, ExpressionToken, TextToken, ExpressionTypeToken

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
                buffer.append(TextExpression(token))
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
        elif token == ExpressionTokens.Unless:
            return self.parse_expression_unless()
        else:
            raise SyntaxError('invalid syntax for expression')

    def parse_expression_equals(self):
        v = self.lexer.next()
        assert isinstance(v, ExpressionToken), v

        # { "type": ExpressionTokens.Equals, "var": v }
        return EqualsExpression(v)

    def parse_expression_table(self):
        v = self.lexer.next()
        assert isinstance(v, ExpressionToken), v

        # { "type": ExpressionTokens.Table, "var": v }
        return TableExpression(v)

    def parse_expression_unless(self):
        condition = self.lexer.next()
        assert isinstance(condition, ExpressionToken), 'invalid token %s' % condition

        consequences = self.parse()

        end = self.lexer.next()
        assert isinstance(end, ExpressionTypeToken) and end == ExpressionTokens.End, 'if missing end'

        endexpr = self.lexer.next()
        assert isinstance(endexpr, ExpressionToken) and endexpr == condition, 'if closed unexpectedly'
        return UnlessExpression(condition, consequences)

    def parse_expression_if(self):
        condition = self.lexer.next()
        assert isinstance(condition, ExpressionToken), 'invalid token %s' % condition

        consequences = self.parse()

        end = self.lexer.next()
        assert isinstance(end, ExpressionTypeToken) and end == ExpressionTokens.End, 'if missing end'

        endexpr = self.lexer.next()
        assert isinstance(endexpr, ExpressionToken) and endexpr == condition, 'if closed unexpectedly'
        return IfExpression(condition, consequences)

class UnlessExpression:
    def __init__(self, condition: ExpressionToken, consequences: list) -> None:
        self.type = ExpressionTokens.Unless
        self.condition = condition
        self.consequences = consequences


class IfExpression:
    def __init__(self, condition: ExpressionToken, consequences: list) -> None:
        self.type = ExpressionTokens.If
        self.condition = condition
        self.consequences = consequences

class EqualsExpression:
    def __init__(self, token):
        self.type = ExpressionTokens.Equals
        self.token = token

class TableExpression:
    def __init__(self, token):
        self.type = ExpressionTokens.Table
        self.token = token


class TextExpression:
    def __init__(self, text) -> None:
        self.type = "text"
        self.text = text


