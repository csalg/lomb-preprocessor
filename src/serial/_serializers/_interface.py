import html
import json
from abc import ABC, abstractmethod

class SerializerABC(ABC):
    
    @abstractmethod
    def __init__(self, filename, source_language, target_language):
        pass

    @abstractmethod
    def get_translation_dictionary(self):
       pass 

    @abstractmethod
    def set_translation_dictionary(self, new_dictionary):
       pass

    @abstractmethod
    def get_lemmas_dictionary(self):
        pass

    @abstractmethod
    def set_lemmas_dictionary(self, new_dictionary):
        pass

    @abstractmethod
    def save_to_file(self, output_filename):
        pass


class Chunk:
    def __init__(self, text, support_text="", tokens_to_lemmas={}):
        self.text = text
        self.support_text = support_text
        self.tokens_to_lemmas = tokens_to_lemmas

    def to_span(self,id):
        tokens_to_lemmas_serialized = html.escape(json.dumps(self.tokens_to_lemmas),quote=True)
        support_text_serialized = html.escape(json.dumps(self.support_text), quote=True)
        return \
            f"<span id='{id}' data-type='dual-language-chunk' data-support-text='{support_text_serialized}' data-tokens-to-lemmas='{tokens_to_lemmas_serialized}' class='dual-language-chunk'>{self.text}</span>"

    def set_tokens_to_lemmas(self, tokens_to_lemmas):
        self.tokens_to_lemmas = tokens_to_lemmas

    def set_support_text(self, support_text):
        self.support_text = support_text

    def _get_lemmas(self):
        return list(self.tokens_to_lemmas.values())