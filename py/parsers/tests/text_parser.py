import sys
from py.readers.text import TextReader
from py.parsers.text import Lexer

def run(filename: str):
    reader = TextReader(filename)
    lex = Lexer(reader)

    while not lex.eof():
        token = lex.read()
        if token is None:
            continue

        print(token)

if __name__ == "__main__":
    run(sys.argv[1])