from typing import List, Union
from py.templater.text import TextTemplateParser

from py.parsers.engine import EqualsExpression, TableExpression, IfExpression, TextExpression, UnlessExpression

TableTemplate = '''
<table>
    <thead>
        <tr>
            %s
        </tr>
    </thead>
    <tbody>
        %s
    </tbody>
</table>
'''

class RenderTable:
    def __init__(self, context):
        self.context = context

    def render(self, token) -> str:
        t = eval(token, self.context)
        assert isinstance(t, dict), 'Invalid data for rendering table'
        header = self.render_header(t.get('headers', []))
        body = self.render_body(t.get('data', []))

        return TableTemplate % (header, body)

    def render_header(self, headers: list):
        return "\n".join(["<th>%s</th>" % header for header in headers])

    def render_body(self, data: list):
        ros = ['<tr>%s</tr>' % "\n".join(['<td>%s</td>' % col for col in row]) for row in data]
        return "\n".join(ros)


class RenderList:
    def __init__(self, context):
        self.context = context

    def render(self, token) -> str:
        t = eval(token, self.context)

        assert isinstance(t, list), 'Invalid data for rendering list'
        return self.render_list(t)

    def render_list(self, items):
        return "<ul>%s</ul>" % "\n".join(["<li>%s</li>" % item for item in items])

class HtmlTemplater(TextTemplateParser):
    def parse_expressions(self, expressions) -> List:
        result = []
        for expr in expressions:
            if not expr:
                continue
            result.extend(self.parse_token(expr))
        return result

    def parse_token(self, expr) -> Union[str, List[str]]:
        if isinstance(expr, EqualsExpression):
            return str(eval(expr.token.val(), self.context))
        if isinstance(expr, TableExpression):
            token = expr.token.val()
            rt = RenderTable(self.context)
            return rt.render(token)
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

        # print(expr, type(expr))
        raise SyntaxError('unparseable code')

