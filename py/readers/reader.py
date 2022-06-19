from abc import ABC, abstractmethod

class Reader(ABC):

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def peek(self):
        pass

    @abstractmethod
    def eof(self):
        pass
