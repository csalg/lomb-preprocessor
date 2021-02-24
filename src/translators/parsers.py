
import re
from abc import ABC, abstractmethod

from logging_ import logger


class ParserABC(ABC):
    @abstractmethod
    def encode_sentence(self, id, sentence):
        pass

    @abstractmethod
    def parse_translated_buffer(self, ids_to_source_sentences, buffer):
        pass

class NewlineParser(ParserABC):
    matchNumbers = re.compile('^\d{4}$')

    def encode_sentence(self, id, sentence):
        return f'{id}\n{sentence}\n'

    def parse_translated_buffer(self, ids_to_source_sentences, buffer):
        logger.debug('Parsing buffer')
        lines = buffer.splitlines()
        buffer_translation_dictionary = {}
        i = 0
        while i < len(lines):
            try:
                source_sentence, translated_sentence, i = self.__parse_next_sentence(ids_to_source_sentences, lines, i)
                buffer_translation_dictionary[source_sentence] = translated_sentence
            except:
               break
        return buffer_translation_dictionary

    def __parse_next_sentence(self, ids_to_source_sentences, lines, i):

        # First we need to find the next valid id.
        id = -1
        while i < len(lines):
            if NewlineParser.matchNumbers.match(lines[i]):
                id = int(lines[i])
            i += 1
            if id in ids_to_source_sentences:
                break


        if id == -1:
            raise Exception("No more sentences to parse")

        # Next we find all the text before the next
        # valid id
        buffer = ""
        while i < len(lines):
            if NewlineParser.matchNumbers.match(lines[i]):
                next_id = int(lines[i])
                if next_id in ids_to_source_sentences:
                    break
            else:
                if buffer:
                    buffer += '\n'
                buffer += lines[i]
                i += 1

        source_sentence = ids_to_source_sentences[id]
        translated_sentence = buffer
        return source_sentence, translated_sentence, i


