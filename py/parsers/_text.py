'''
from enum import Enum

PERCENTAGE = "%"

TEMPLATE_START = "{%"
TEMPLATE_END = "%}"
TEMPLATE_VAR_BLOCK = "{%="
TEMPLATE_IF_BLOCK = "{%#"
TEMPLATE_END_BLOCK = "{%/"
TEMPLATE_TABLE_BLOCK = "{%@"

TEMPLATE_VAR = "="
TEMPLATE_IF = "#"
TEMPLATE_IF_END = "/"
TEMPLATE_TABLE = "@"

WHITESPACE = [' ', '\t', '\b', '\n', '\r']
TEMPLATE_SYNTAXES = [TEMPLATE_VAR_BLOCK, TEMPLATE_IF_BLOCK, TEMPLATE_END_BLOCK, TEMPLATE_TABLE_BLOCK]

class TokenizeTextTemplate:
    def __init__(self):
        self.chars = []

    def read(self, c):
        self.chars.append(c)

        token_so_far = ''.join(self.chars)
        if token_so_far in TEMPLATE_SYNTAXES:
            return token_so_far



class ParseTextTemplate:
    def __init__(self):
        self.state = 
    
    def read_token(self, token):


def lex_template(string):
    code = ''

    # print("sss", string)
    if string.startswith(TEMPLATE_START):
        code += TEMPLATE_START
        spaces, string = lex_gaps(string[2:])
        code = code + spaces

        # print("code", code, "s", string)
        c = string[0]
        print("C", c)

        if c == TEMPLATE_VAR:
            variable, string = lex_variable(string)
            code = code + variable
        elif c == TEMPLATE_TABLE:
            variable, string = lex_variable(string)
            code = code + variable
        elif c == TEMPLATE_IF:
            variable, string = lex_if(string)
            code = code + variable

        return code, string
    return None, string

def lex_variable(string):
    # print("lexing variable")

    variable = ''
    for c in string:
        if c != PERCENTAGE:
            variable = variable + c
            continue
        break

    variable = variable + TEMPLATE_END
    return variable, string[len(variable)+1:]


def lex_if(string):
    code = ''

    for c in string:
        if c != PERCENTAGE:
            code += c
            continue
        break

    condition_var = code.replace(TEMPLATE_IF, "").strip()
    print("code", code)

    string = string[len(code)+2:]

    # read everything unitl its start of a template
    # if start_of_template + peek(1) not {%/ then call lex_template()
    # else check if the name is same as condition_var
    # if yes, return
    # else throw error
    return code, string[len(code)+1:]

def is_template_start(string):
    if len(string) < 2:
        return False
    return "{%%" == "%s%s" % (string[0], string[1])

def lex_gaps(string):
    spaces = ''
    for c in string:
        if c in WHITESPACE:
            spaces = spaces + c
        else:
            break

    return spaces, string[len(spaces):]


def lex_everything_else(string):
    # print("lex everything else")
    text = ''

    i = string.find(TEMPLATE_START)
    if i > -1:
        text = string[:i]
        return text, string[len(text):]

    return string, []

def lex(string):
    tokens = []
    # print(string)

    while len(string):
        template_str, string = lex_template(string)
        if template_str is not None:
            print("tt", template_str)
            continue

        text, string = lex_everything_else(string)
        if text is not None:
            print("text", text)

        c = string[0]

        if c in WHITESPACE:
            string = string[1:]
            continue
''''
