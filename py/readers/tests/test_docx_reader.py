import sys
from py.readers.docx import DocxReader

def print_table(table):
    ls =[]
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                ls.append(paragraph.text)
    print(', '.join(ls))

def run(filename):
    r = DocxReader(filename)

    while not r.eof():
        print(r.read().text)

    for table in r.doc.tables:
        print_table(table)


if __name__ == "__main__":
    run(sys.argv[1])
