from abc import ABC, abstractmethod

class ITagger(ABC):
    def __init__(self, processor=None):
        self.processor = processor

    @abstractmethod
    def tag(self, sentence_dictionary):
        pass

