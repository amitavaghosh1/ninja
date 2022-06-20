import sys
from types import SimpleNamespace

from py.templater.text import TextTemplateParser

def run(filename):
    context = {
        "date": "2023-09-01",
        "hasEmail": True,
        "isGoogleEmail": False,
        "table_data": {"a": 1, "b": 2},
        "user": SimpleNamespace(**{"fullname": "A B"})
    }
    t = TextTemplateParser(filename, context)
    print(t.parse())

if __name__ == "__main__":
    run(sys.argv[1])
