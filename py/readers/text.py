from py.readers.reader import Reader

class TextReader(Reader):
    def __init__(self, filename):
        self.string = __read_text_file__(filename)
        self.strlen = len(self.string)
        self.index = 0

    def read(self):
        if self.strlen <= self.index:
            return None

        c = self.string[self.index]
        self.index += 1
        return c

    def peek(self):
        if self.strlen < self.index:
            return None
        return self.string[self.index]

    def eof(self):
        return self.index >= self.strlen


def __read_text_file__(filename: str):
    with open(filename, 'rb') as f:
        try:
            data = f.read().decode('windows-1252')
            return data
        except:
            pass

        try:
            data = f.read().decode('utf-8')
            return data
        except:
            return ""

