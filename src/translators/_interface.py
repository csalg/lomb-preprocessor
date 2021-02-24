from abc import ABC, abstractmethod


class ITranslator(ABC):
    def __init__(self, source_language, target_language):
        self.source_language = source_language
        self.target_language = target_language

    @abstractmethod
    def translate(self, translation_dictionary):
        pass