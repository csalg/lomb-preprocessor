import json

class Chunk:
    def __init__(self, text, support_text="", tokens_to_lemmas={}):
        self.text = text
        self.support_text = support_text
        self.tokens_to_lemmas = tokens_to_lemmas

    def to_span(self):
        tokens_to_lemmas_serialized = json.dumps(self.tokens_to_lemmas)
        support_text_serialized = json.dumps(self.support_text)
        return \
            f"<span data-type='dual-language-chunk' data-support-text='{support_text_serialized}' data-tokens-to-lemmas='{tokens_to_lemmas_serialized}' class='dual-language-chunk'>{self.text}</span>"

    def set_tokens_to_lemmas(self, tokens_to_lemmas):
        self.tokens_to_lemmas = tokens_to_lemmas

    def set_support_text(self, support_text):
        self.support_text = support_text

    def _get_lemmas(self):
        return list(self.tokens_to_lemmas.values())
