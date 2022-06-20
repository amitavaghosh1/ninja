from docx import Document

from py.readers.reader import Reader

class DocxReader(Reader):
    def __init__(self, filename):
        self.filename = filename
        self.doc = Document(filename)

        print(type(self.doc))
        self.lines = self.doc.paragraphs
        self.index = 0

    def read(self):
        if len(self.lines) <= self.index:
            return None

        c = self.lines[self.index]
        self.index += 1
        return c

    def peek(self):
        if len(self.lines) <= self.index:
            return None

        return self.lines[self.index]

    def eof(self):
        return self.index >= len(self.lines)

