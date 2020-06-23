from abc import ABC, abstractmethod
import os
from copy import copy

import spacy

from .regex import *


class Tagger(ABC):
    def __init__(self, processor=None):
        self.processor = processor

    @abstractmethod
    def tag(self, sentence_dictionary):
        pass


class GermanTagger(Tagger):
    def __init__(self, processor=None):
        self.processor = processor if processor else spacy.load('de_core_news_sm')
        self._load_german_prepositions()

    def tag(self, sentence_dictionary):
        for sentence in sentence_dictionary:
            sentence_dictionary[sentence] = self._make_token_dictionary(sentence)
        pass

    def _load_german_prepositions(self):
        prepositions_file = os.getcwd() + '/config' + '/german_separable_verb_prepositions.txt'
        with open(prepositions_file) as file:
            self.prepositions = file.read().splitlines()

    def _make_token_dictionary(self, sentence):

        phrases = breaks_into_phrases_to_detect_separable_verbs.split(sentence)
        token_dictionary = {}

        for phrase in phrases:
            tokens = self.processor(phrase)
            if not tokens:
                continue
            separable_verb_tokens, separable_verb_lemma = self.__find_possible_separable_verbs(tokens)

            for token in tokens:
                token, lemma = str(token), token.lemma_
                if matches_punctuation.match(token):
                    continue
                if token in separable_verb_tokens:
                    token_dictionary[token] = separable_verb_lemma
                    continue
                token_dictionary[token] = lemma

        return token_dictionary

    def __find_possible_separable_verbs(self, tokens):
        final_word = tokens[-1].lemma_
        if final_word in self.prepositions:
            for token in tokens:
                if token.tag_[0] == 'V':
                    tokens = [final_word, str(token)]
                    lemma = final_word + token.lemma_
                    return tokens, lemma
        return [], ""