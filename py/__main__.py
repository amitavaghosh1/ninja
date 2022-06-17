import sys
from py.readers.text import read_text_file
from py.templater.template import TextTemplate
from py.parsers.text import lex

file = sys.argv[1]
print(file)

data = read_text_file(file)

tt = lex(data)

