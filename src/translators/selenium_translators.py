import logging
import time
from random import random

from config import MAX_CHARACTERS_PER_BUFFER, MAX_TIMEOUTS_BEFORE_ASSUMING_TEMPORARY_BAN, WAIT_FOR_IP_UNBLOCK, \
    MAX_NUMBER_OF_REQUESTS_WITH_SAME_DRIVER, WAIT_BETWEEN_DRIVER_CHANGE, MAX_TRANSLATION_ITERATIONS
from logging_ import logger
from translators.agents import SeleniumAgentABC, TIMEOUT_EXCEPTION, TEMPORARY_BAN_EXCEPTION, \
    UNKNOWN_EXCEPTION
from translators.parsers import ParserABC
from translators._util import PersistedDictionary
from util import print_progress_bar


class SeleniumTranslator():
    def __init__(self,
                 source_language : str,
                 target_language : str,
                 parser_constructor,
                 agent_constructor
                 ):
        self.source_language = source_language
        self.target_language = target_language
        self.parser : ParserABC = parser_constructor()
        self.agent : SeleniumAgentABC = agent_constructor(source_language, target_language)
        self.__current_sentence_id = int(random() * 10000)

    def translate(self, translation_dictionary, iterations=0):
        translation_dictionary = PersistedDictionary(translation_dictionary)

        self.agent.start()
        requests_with_same_driver = 0
        buffer = ""
        ids_to_source_sentences = {}
        for source_sentence, target_sentence in translation_dictionary.items():
            if target_sentence:
                continue

            sentence_id = self.__next_id()
            ids_to_source_sentences[sentence_id] = source_sentence
            source_sentence_encoded = self.parser.encode_sentence(sentence_id, source_sentence)
            if len(buffer+source_sentence_encoded) > MAX_CHARACTERS_PER_BUFFER:
                if len(buffer) > MAX_CHARACTERS_PER_BUFFER:
                    logging.warning('Found a sentence that was too large to translate. skipping')
                    buffer = ""
                else:
                    if requests_with_same_driver == MAX_NUMBER_OF_REQUESTS_WITH_SAME_DRIVER:
                        self.agent.close()
                        time.sleep(WAIT_BETWEEN_DRIVER_CHANGE)
                        self.agent.start()
                        requests_with_same_driver = 0
                    new_translations = self.__buffer_to_new_translations(ids_to_source_sentences, buffer)
                    translation_dictionary.update(new_translations)
                    print_progress_bar(len_with_value(translation_dictionary.values()), len_with_value(translation_dictionary.keys()))
                    buffer = ""
                    requests_with_same_driver += 1
            buffer += '\n' + source_sentence_encoded

        if buffer:
            new_translations = self.__buffer_to_new_translations(ids_to_source_sentences, buffer)
            translation_dictionary.update(new_translations)
        if len(self.__translation_dictionary_contains_empty_values(translation_dictionary)):
            logger.info('Empty values found in dictionary after translation')
            logger.info(self.__translation_dictionary_contains_empty_values(translation_dictionary))
            logger.info(f'Iterations {iterations}/{MAX_TRANSLATION_ITERATIONS}')
            if iterations < MAX_TRANSLATION_ITERATIONS:
                logger.info('New translation pass will be called.')
                return self.translate(translation_dictionary, iterations=iterations+1)
            else:
                logger.warning('Max number of iterations reached. Giving up.')

        print_progress_bar(len_with_value(translation_dictionary.values()),
                           len_with_value(translation_dictionary.keys()))
        return translation_dictionary

    def __next_id(self):
        self.__current_sentence_id += 1
        self.__current_sentence_id = self.__current_sentence_id % 9000
        return self.__current_sentence_id + 1000

    def __buffer_to_new_translations(self,ids_to_source_sentences, buffer):
        if len(buffer) > MAX_CHARACTERS_PER_BUFFER + 100:
            raise Exception(f'Buffer length {len(buffer)} exceeds the limit ({MAX_CHARACTERS_PER_BUFFER})')
        timeouts = 1
        while True:
            try:
                translated_buffer = self.agent.translate_buffer(buffer)
                logger.debug('Received translated buffer in translator. Will parse.')
                new_translations = self.parser.parse_translated_buffer(ids_to_source_sentences, translated_buffer)
                logger.debug('Translations parsed')
                logger.debug(new_translations)
                return new_translations
            except TEMPORARY_BAN_EXCEPTION as e:
                logger.warning(str(e))
                logger.warning(f'Sleeping {WAIT_FOR_IP_UNBLOCK / 60} minutes.')
                time.sleep(WAIT_FOR_IP_UNBLOCK)
            except (UNKNOWN_EXCEPTION, TIMEOUT_EXCEPTION) as e:
                logger.warning(str(e))
                if timeouts == MAX_TIMEOUTS_BEFORE_ASSUMING_TEMPORARY_BAN:
                    logger.warning(f'Timeouts: {timeouts} / {MAX_TIMEOUTS_BEFORE_ASSUMING_TEMPORARY_BAN}. Assuming temporary ban')
                    logger.warning(f'Sleeping {WAIT_FOR_IP_UNBLOCK/60} minutes.')
                    time.sleep(WAIT_FOR_IP_UNBLOCK)
                logger.warning(f'Timeout {timeouts}/{MAX_TIMEOUTS_BEFORE_ASSUMING_TEMPORARY_BAN}')
                timeouts+=1

    def __translation_dictionary_contains_empty_values(self, translation_dictionary):
        return list(filter(lambda x : bool(x[0].strip('\n')) and not bool(x[1]), translation_dictionary.items()))


def len_with_value(values):
    with_values = list(filter(lambda x : bool(x.strip('\n')), values))
    return len(with_values)


