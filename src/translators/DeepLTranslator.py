import json
import logging
import os
import re
from abc import ABC, abstractmethod
from shutil import which
from random import randint
from time import sleep
from datetime import datetime, timedelta
import pickle

from selenium import webdriver  
from selenium.webdriver.chrome.options import Options

from config import HEADLESS_MODE
from .TranslatorABC import TranslatorABC
from .util import to_deepl_language

SENTENCE_SEPARATOR = "\n-&----&-\n"
ID_SEPARATOR = "\n"
MIN_WAIT_FOR_TRANSLATION = 5
MAX_WAIT_FOR_TRANSLATION = 60
MAX_CHARACTERS_PER_BUFFER = 3200
MAX_NUMBER_OF_REQUESTS_WITH_SAME_DRIVER = 30
WAIT_BETWEEN_DRIVER_CHANGE = 120
MAX_TIMEOUTS_BEFORE_ASSUMING_TEMPORARY_BAN = 5
SELENIUM_TIMEOUT = MAX_WAIT_FOR_TRANSLATION
URL = "http://www.deepl.com"
MINIMUM_ACCEPTABLE_TRANSLATION_RATIO = 0.2
WAIT_FOR_IP_UNBLOCK = 60*60
TRANSLATION_DICTIONARY_FILENAME = 'translation_dictionary.pkl'


logging.basicConfig(level=logging.INFO)

class DeepLTranslator(TranslatorABC):
    def __init__(self, source_language, target_language, interaction_agent_constructor):
        super().__init__(source_language,target_language)
        self.interaction = interaction_agent_constructor(source_language, target_language)

    def translate(self, translation_dictionary):
        translation_dictionary = PersistedDictionary(translation_dictionary)

        for sentence in translation_dictionary.keys():
            if translation_dictionary[sentence]:
                continue
            try:
                self.interaction.add(sentence)
            except:
                translated_sentences= self.interaction.dispatch_translation()
                translation_dictionary.update(translated_sentences)
                try:
                    self.interaction.add(sentence)
                except:
                    logging.warning(f'Failed to add chunk of length {len(sentence)}')

        translated_sentences = self.interaction.dispatch_translation()
        translation_dictionary.update(translated_sentences)
        translation_dictionary.delete_pickle()
        return translation_dictionary


class InteractionAgentABC:
    """
    High level orchestration class which delegates the implementation details downstream.
    """

    def __init__(self,source_language,target_language):
        self.source_language = source_language
        self.target_language = target_language

        self.buffer = ""
        self.id_to_source_sentence = {}
        self.current_sentence_id = randint(1000, 1999)
        self.browser = WebsiteInteractionAdaptor(source_language, target_language)
        self.number_of_requests = 0
        self.number_of_timeouts = 0

    def add(self, sentence):
        adapted_sentence = self._encode_sentence(sentence, self.current_sentence_id)
        if len(self.buffer + adapted_sentence) > MAX_CHARACTERS_PER_BUFFER:
            raise Exception(f'Adding "{sentence}" overflows max characters per buffer')
        self.buffer += adapted_sentence
        self.id_to_source_sentence[self.current_sentence_id]=sentence
        self.current_sentence_id+=1
        self.current_sentence_id = 1000 if self.current_sentence_id == 10000 else self.current_sentence_id


    def dispatch_translation(self):
        self.number_of_requests += 1
        logging.info(f'Requests without closing browser: {self.number_of_requests}')
        self.__reset_driver_if_number_of_interactions_exceeded()
        try:
            translated_buffer = self.browser.translate_buffer(self.buffer)
            self.buffer = ""
            return self._parse_translated_buffer(translated_buffer)
        except DialogInteractionABC.TEMPORARY_BAN_EXCEPTION as exception:
            logging.warning(exception)
            return self.__block_on_ip_blocked_and_resume()
        except DialogInteractionABC.TIMEOUT_EXCEPTION as exception:
            logging.info(f"Timeout {self.number_of_timeouts} / {MAX_TIMEOUTS_BEFORE_ASSUMING_TEMPORARY_BAN}: ", exception)
            if self.number_of_timeouts < MAX_TIMEOUTS_BEFORE_ASSUMING_TEMPORARY_BAN:
                self.restart_browser()
                self.number_of_timeouts += 1
                return self.dispatch_translation()
            else:
                logging.warning("Maximum number of timeouts exceeded. Assuming a temporary IP ban.")
                return self.__block_on_ip_blocked_and_resume()

    def __reset_driver_if_number_of_interactions_exceeded(self):
        if self.number_of_requests >= MAX_NUMBER_OF_REQUESTS_WITH_SAME_DRIVER:
            logging.info('Resetting driver')
            sleep(WAIT_BETWEEN_DRIVER_CHANGE)
            self.restart_browser()
            logging.info('Driver was reset')

    def __block_on_ip_blocked_and_resume(self):
        self.__block_on_ip_blocked()
        self.number_of_timeouts = 0
        self.number_of_requests = 0
        return self.dispatch_translation()

    def reset(self):
        self.buffer = ""
        self.id_to_source_sentence = {}
        self.number_of_requests = 0
        self.number_of_timeouts = 0

    def restart_browser(self):
        self.number_of_requests = 0
        self.browser.close()
        sleep(WAIT_BETWEEN_DRIVER_CHANGE)
        self.browser.start()


    def __block_on_ip_blocked(self):
        self.browser.close()
        time_to_resume = datetime.now() + timedelta(seconds=WAIT_FOR_IP_UNBLOCK)
        time_to_resume_str = time_to_resume.strftime('%H:%M:%S')
        logging.warning(f"Blocking until {time_to_resume_str} minutes because ip was blocked.")
        sleep(WAIT_FOR_IP_UNBLOCK)
        self.browser.start()

    def _encode_sentence(self, sentence, id):
        return f'{id}{ID_SEPARATOR}{sentence}{SENTENCE_SEPARATOR}'

    def _parse_translated_buffer(self, buffer):
        logging.info('Old interaction agent')
        raw_sentences = buffer.split(SENTENCE_SEPARATOR)
        buffer_translation_dictionary = {}
        sentences = map(lambda raw_sentence: IdAndTranslation(raw_sentence), raw_sentences)
        for sentence in sentences:
            id = sentence.id
            if id in self.id_to_source_sentence:
                source_sentence = self.id_to_source_sentence[id]
                target_sentence = sentence.text
                buffer_translation_dictionary[source_sentence] = target_sentence
        return buffer_translation_dictionary


class DialogInteractionABC(ABC):
    """
    This is an adaptor between the 'language' of the website, and a language of successful attempts
    or exceptions that can be reasoned about.
    The factory method dispatch has to be implemented.
    """

    class TEMPORARY_BAN_EXCEPTION(Exception):
        def __init__(self):
            super().__init__ ('The server has temporarily banned this ip.')

    class TIMEOUT_EXCEPTION(Exception):
        def __init__(self):
            super().__init__ (f"Waited for translation for {MAX_WAIT_FOR_TRANSLATION} seconds. Giving up.")

    class UNKNOWN_EXCEPTION(Exception):
        def __init__(self):
            super().__init__ ('The request failed for unknown reasons.')

    class EXCEPTION_INSERTING_TEXT(Exception):
        def __init__(self, buffer, original_exception):

            super().__init__ (f'Exception {original_exception} inserting {buffer}')

    def __init__(self, source_language, target_language, ):
        self.source_language = source_language
        self.target_language = target_language

    @abstractmethod
    def translate_buffer(self, source_buffer):
        pass


class WebsiteInteractionAdaptor(DialogInteractionABC):
    """
    This is an adaptor between the 'language' of the website, and
    exceptions we can reason about and handle.
    """

    def __init__(self, source_language, target_language, ):
        super(WebsiteInteractionAdaptor, self).__init__(source_language, target_language)
        self.start()

    def start(self):
        self.driver = WebsiteInteractionAdaptor.__make_headless_selenium_driver()
        self.driver.get(URL)

    def close(self):
        self.driver.close()

    def restart(self):
        self.close()
        self.start()

    def translate_buffer(self, source_buffer):
        source_textarea = self.driver.find_elements_by_class_name("lmt__source_textarea")[0]
        print(source_buffer)
        self.__insert_source_buffer_in_textarea(source_buffer, source_textarea)

        translated_buffer = ""
        while len(translated_buffer) / len(source_buffer) < MINIMUM_ACCEPTABLE_TRANSLATION_RATIO:
            try:
                source_textarea.send_keys('  ')
            except Exception as e:
                logging.warning(e)
            self.__block_until_translation_received()
            target_textarea = self.driver.find_elements_by_class_name("lmt__target_textarea")[0]
            translated_buffer = str(target_textarea.get_attribute('value'))

        return translated_buffer

    def __insert_source_buffer_in_textarea(self, source_buffer, source_textarea):
        _, target_lang = to_deepl_language(self.source_language), to_deepl_language(self.target_language)
        while True:
            try:
                sleep(1)
                source_textarea.send_keys('  ')
                sleep(2)
                source_textarea.send_keys('  \n')
                break
            except Exception as e:
                logging.warning(e)
        try:
            print(target_lang)
            escaped_buffer = source_buffer.replace('`', '').replace('$', "S").replace("\\", "\\\\")
            self.driver.execute_script(f'''
            var cookiesButton = document.querySelector('button.dl_cookieBanner--buttonAll');
            if (cookiesButton) cookiesButton.click();
            //document.querySelector('button[dl-test="translator-source-lang-btn"]').click();
            //document.querySelector('div[dl-test="translator-source-lang-list"]>button[dl-test="translator-lang-option-{self.source_language.lower()}"]').click();
            //document.querySelector('button[dl-test="translator-target-lang-btn"]').click();
            //document.querySelector('div[dl-test="translator-target-lang-list"]>button[dl-test="translator-lang-option-{target_lang}"]').click();
            var source_textarea = document.getElementsByClassName("lmt__source_textarea")[0];
            source_textarea.value = `{escaped_buffer}`
            source_textarea.dispatchEvent(new Event('change'))
            document.querySelector('button[dl-test="translator-source-lang-btn"]').click();
            document.querySelector('div[dl-test="translator-source-lang-list"]>button[dl-test="translator-lang-option-{self.source_language.lower()}"]').click();
            document.querySelector('button[dl-test="translator-target-lang-btn"]').click();
            document.querySelector('div[dl-test="translator-target-lang-list"]>button[dl-test="translator-lang-option-{target_lang}"]').click();
            // document.querySelector('button[dl-lang="{self.source_language.upper()}"]').click();
            // document.querySelector('div[dl-test="translator-target-lang-list"]>button[dl-test="translator-lang-option-{target_lang}"]').click();
            ''')
        except Exception as e:
            raise WebsiteInteractionAdaptor.EXCEPTION_INSERTING_TEXT(source_buffer, e)

    def __check_ip_blocked(self):
        try:
            self.driver.find_element_by_class_name("lmt__notification__blocked")
            return True
        except:
            return False

    def __block_until_translation_received(self):
        start_time = datetime.now()
        max_time = start_time + timedelta(seconds=MAX_WAIT_FOR_TRANSLATION)
        min_time = start_time + timedelta(seconds=MIN_WAIT_FOR_TRANSLATION)
        while True:
            sleep(1)
            if datetime.now() < min_time:
                continue
            if datetime.now() > max_time:
                if self.__check_ip_blocked():
                    raise WebsiteInteractionAdaptor.TEMPORARY_BAN_EXCEPTION
                raise WebsiteInteractionAdaptor.TIMEOUT_EXCEPTION
            progress_popup = self.driver.find_elements_by_class_name('lmt__progress_popup')[0]
            target_textarea = self.driver.find_elements_by_class_name('lmt__target_textarea')[0]
            if progress_popup.value_of_css_property('display') == 'none' and \
                    target_textarea.get_attribute('value'):
                return

    @staticmethod
    def __make_headless_selenium_driver():
        binary_path = which('chromedriver')
        options = Options()
        if HEADLESS_MODE:
            options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=binary_path,
                                  chrome_options=options)
        driver.implicitly_wait(SELENIUM_TIMEOUT)
        return driver


class PersistedDictionary(dict):
    """
    Extends the dictionary class to have disk persistence as a pickle.
    """

    def __init__(self, dictionary, **kwargs):
        if PersistedDictionary.__already_exists():
            dictionary = PersistedDictionary.__restore(dictionary)
        super().__init__(dictionary, **kwargs)

    def update(self,*args, **kwargs):
        super(PersistedDictionary, self).update(*args,**kwargs)
        self.persist()

    def persist(self):
        with open(TRANSLATION_DICTIONARY_FILENAME, 'wb') as file:
            pickle.dump(self, file)

    def delete_pickle(self):
        if os.path.exists(TRANSLATION_DICTIONARY_FILENAME):
            os.remove(TRANSLATION_DICTIONARY_FILENAME)

    @staticmethod
    def __already_exists():
        return os.path.exists(TRANSLATION_DICTIONARY_FILENAME)

    @staticmethod
    def __restore(translation_dictionary):

        if os.path.exists(TRANSLATION_DICTIONARY_FILENAME):
            with open(TRANSLATION_DICTIONARY_FILENAME, 'rb') as file:
                restored_dictionary = pickle.load(file)

            for key in translation_dictionary.keys():
                if key in restored_dictionary:
                    if restored_dictionary[key]:
                        translation_dictionary[key]=restored_dictionary[key]

        return translation_dictionary


class IdAndTranslation():
    def __init__(self, raw_phrase):
        if raw_phrase == "":
            self.make_null_object()
            return 

        while raw_phrase[0] == '\n':
            raw_phrase = raw_phrase[1:]
            if raw_phrase == "":
                self.make_null_object()
                return 
        try:
            self.id, self.text = raw_phrase.split(ID_SEPARATOR,1)
        except:
            self.make_null_object()
            return 
        try:
            self.id = int(self.id)
        except:
            self.id = -1

    def make_null_object(self):
        self.id = -1
        self.text = ""


class ChineseInteractionAgent(InteractionAgentABC):
    matchNumbers = re.compile('^\d{4}$')

    def __init__(self, *args, **kwargs):
        super(ChineseInteractionAgent, self).__init__(*args, **kwargs)

    def _encode_sentence(self, sentence, id):
        return f'{id}\n{sentence}\n'

    def _parse_translated_buffer(self, buffer):
        lines = buffer.splitlines()
        logging.info(lines)
        buffer_translation_dictionary = {}
        currentId = ""
        currentSentence = ""
        i = 0
        # Look for first id and sentence
        while i < len(lines):
            if not currentId:
                if bool(ChineseInteractionAgent.matchNumbers.match(lines[i])):
                    logging.info('Matched')
                    currentId = lines[i]
                    i += 1
                    break
            i += 1

        # Process remainder of buffer
        while i < len(lines):
            if ChineseInteractionAgent.matchNumbers.match(lines[i]):
                id = int(currentId)
                if id in self.id_to_source_sentence:
                    source_sentence = self.id_to_source_sentence[id]
                    logging.info(f'Parsed: \n{source_sentence}\n{currentSentence}')
                    buffer_translation_dictionary[source_sentence] = currentSentence
                    currentSentence = ""
                currentId = lines[i]
            else:
                currentSentence += lines[i]
            i += 1

        return buffer_translation_dictionary
