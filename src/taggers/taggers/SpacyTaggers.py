from abc import ABC, abstractmethod
import os
from copy import copy

import spacy

from taggers.regex import matches_punctuation
from taggers.taggers.TaggerABC import TaggerABC


class BaseSpacyTagger(TaggerABC):
    def __init__(self, processor=lambda : None):
        super().__init__(processor())

    def tag(self, sentence_dictionary):
        for sentence in sentence_dictionary:
            sentence_dictionary[sentence] = self._make_token_dictionary(sentence)
        return sentence_dictionary

    def _make_token_dictionary(self, sentence):
        token_dictionary = {}
        tokens = self.processor(sentence)
        if not tokens:
            return token_dictionary

        for token in tokens:
            token, lemma = str(token), token.lemma_
            if matches_punctuation.match(token):
                continue
            token_dictionary[token] = lemma

        return token_dictionary


class SpanishTagger(BaseSpacyTagger):
    def __init__(self):
        super(SpanishTagger, self).__init__( lambda : spacy.load('es_core_news_lg'))


class EnglishTagger(BaseSpacyTagger):
    def __init__(self):
        super(EnglishTagger, self).__init__( lambda : spacy.load('en_core_web_md'))


class FrenchTagger(BaseSpacyTagger):
    def __init__(self):
        super(FrenchTagger, self).__init__( lambda : spacy.load('fr_core_news_lg'))


class DanishTagger(BaseSpacyTagger):
    def __init__(self):
        super(DanishTagger, self).__init__( lambda : spacy.load('da_core_news_lg'))

