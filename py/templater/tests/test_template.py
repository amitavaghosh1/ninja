import sys
from types import SimpleNamespace

from py.templater.text import TextTemplateParser
from py.templater.html import HtmlTemplater

def run(filename):
    context = {
        "date": "2023-09-01",
        "hasEmail": True,
        "isGoogleEmail": False,
        "table_data": {"headers": ["name", "email", "active"], "data": [["a", "a@b.c", "true"], ["b", "c.d@e", "false"]]},
        "user": SimpleNamespace(**{"fullname": "A B", "address": "Somewhere"})
    }
    # t = TextTemplateParser(filename, context)
    t = HtmlTemplater(filename, context)
    print(t.parse())

if __name__ == "__main__":
    run(sys.argv[1])
