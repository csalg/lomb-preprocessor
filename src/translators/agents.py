import logging
import time
from abc import abstractmethod, ABC
from datetime import datetime, timedelta

from config import MAX_WAIT_FOR_TRANSLATION, MINIMUM_ACCEPTABLE_TRANSLATION_RATIO, MIN_WAIT_FOR_TRANSLATION
from translators.util import make_headless_selenium_driver


class AgentABC(ABC):

    def __init__(self, source_language, target_language):
        self.source_language = source_language
        self.target_language = target_language

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def translate_buffer(self, buffer):
        pass


class TEMPORARY_BAN_EXCEPTION(Exception):
    def __init__(self):
        super().__init__('The server has temporarily banned this ip.')


class TIMEOUT_EXCEPTION(Exception):
    def __init__(self):
        super().__init__(f"Waited for translation for {MAX_WAIT_FOR_TRANSLATION} seconds. Giving up.")


class UNKNOWN_EXCEPTION(Exception):
    def __init__(self):
        super().__init__('The request failed for unknown reasons.')


class EXCEPTION_INSERTING_TEXT(Exception):
    def __init__(self, buffer, original_exception):
        super().__init__(f'Exception {original_exception} inserting {buffer}')


class GoogleTranslateAgent(AgentABC):
    language_names = {
        'dk': 'da',
    }

    def start(self):
        self.driver = make_headless_selenium_driver()

    def close(self):
        self.driver.close()

    def restart(self):
        self.close()
        self.start()

    def translate_buffer(self, buffer):

        self.driver.get(self.__url())
        time.sleep(2)
        try:
            textarea = self.driver.find_element_by_css_selector('textarea')
            textarea.click()
            self.driver.execute_script(f'''
            const textarea = document.querySelector('textarea')
            textarea.click()
            textarea.value = `{buffer}`
            ''')
        except Exception as e:
            raise EXCEPTION_INSERTING_TEXT(buffer, e)

        translated_buffer = ""
        while len(translated_buffer) / len(buffer) < MINIMUM_ACCEPTABLE_TRANSLATION_RATIO:
            try:
                textarea.send_keys('  ')
            except Exception as e:
                logging.warning(e)
                continue

            translated_buffer = self.__block_until_translation_received(source_buffer_length=len(buffer))
        return translated_buffer

    def __url(self):
        if self.source_language in GoogleTranslateAgent.language_names:
            self.source_language = GoogleTranslateAgent.language_names[self.source_language]
        if self.target_language in GoogleTranslateAgent.language_names:
            self.target_language = GoogleTranslateAgent.language_names[self.target_language]

        return f"https://translate.google.com/#view=home&op=translate&sl={self.source_language}&tl={self.target_language}"

    def __block_until_translation_received(self, source_buffer_length=1):
        start_time = datetime.now()
        max_time = start_time + timedelta(seconds=MAX_WAIT_FOR_TRANSLATION)
        min_time = start_time + timedelta(seconds=MIN_WAIT_FOR_TRANSLATION)

        while True:
            time.sleep(1)
            if datetime.now() < min_time:
                continue
            if max_time < datetime.now():
                raise TIMEOUT_EXCEPTION()
            try:
                translated_buffer = self.__get_result_method1()
            except:
                translated_buffer = self.__get_result_method2()
            print('Translated buffer')
            print(translated_buffer)
            if MINIMUM_ACCEPTABLE_TRANSLATION_RATIO < (len(translated_buffer) / source_buffer_length):
                return translated_buffer

    def __get_result_method1(self):
        # result = self.driver.find_element_by_css_selector('.result-shield-container')
        result = self.driver.find_element_by_css_selector(f'span[lang="{self.target_language}"]')
        return result.get_attribute("innerText")

    def __get_result_method2(self):
        result = self.driver.find_element_by_css_selector('div[data-language]')
        return result.get_attribute("innerText")
