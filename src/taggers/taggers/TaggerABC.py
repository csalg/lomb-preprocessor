from abc import ABC, abstractmethod

class TaggerABC(ABC):
    def __init__(self, processor=None):
        self.processor = processor

    @abstractmethod
    def tag(self, sentence_dictionary):
        pass

