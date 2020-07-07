from abc import ABC, abstractclassmethod

class TranslatorABC(ABC):
    def __init__(self, source_language, target_language):
        self.source_language = source_language
        self.target_language = target_language

    @abstractclassmethod
    def translate(self, translation_dictionary):
        pass