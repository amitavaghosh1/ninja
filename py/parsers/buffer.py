from copy import deepcopy

class ArrayBuffer:
    def __init__(self):
        self.buf = []

    def append(self, v):
        self.buf.append(v)

    def pop(self):
        return self.buf.pop()

    def drain(self):
        result = deepcopy(self.buf)
        self.buf = []
        return result

    def __str__(self):
        return "[ %s ]" % ', '.join(self.buf)


