from abc import ABC, abstractclassmethod

class TranslatorABC(ABC):
    @abstractclassmethod
    def __init__(self, source_language, target_language):
        pass

    @abstractclassmethod
    def translate(self):
        pass