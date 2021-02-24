import logging
import time
from abc import abstractmethod, ABC
from datetime import datetime, timedelta

from selenium.webdriver import ActionChains

from config import MAX_WAIT_FOR_TRANSLATION, MINIMUM_ACCEPTABLE_TRANSLATION_RATIO, MIN_WAIT_FOR_TRANSLATION
from logging_ import logger
from translators.util import make_headless_selenium_driver, to_deepl_language


class SeleniumAgentABC(ABC):
    def __init__(self, source_language, target_language):
        self.source_language = source_language
        self.target_language = target_language

    def start(self):
        self.driver = make_headless_selenium_driver()

    def close(self):
        self.driver.close()

    def restart(self):
        self.close()
        self.start()

    def translate_buffer(self, buffer):

        self.driver.get(self._url())
        time.sleep(2)
        try:
            textarea = self._insert_buffer(buffer)
        except Exception as e:
            raise EXCEPTION_INSERTING_TEXT(buffer, e)

        translated_buffer = ""
        while len(translated_buffer) / len(buffer) < MINIMUM_ACCEPTABLE_TRANSLATION_RATIO:
            try:
                textarea.send_keys('  ')
            except Exception as e:
                logging.warning(e)
                continue
            translated_buffer = self._block_until_translation_received(source_buffer_length=len(buffer))
        logger.debug('Buffer was successfully translated')
        return translated_buffer

    @abstractmethod
    def _url(self):
        pass

    @abstractmethod
    def _insert_buffer(self, buffer):
        pass

    def _block_until_translation_received(self, source_buffer_length=1):
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
                translated_buffer = self._get_result()
                logger.debug('Got translation buffer')
            except:
                continue
            if MINIMUM_ACCEPTABLE_TRANSLATION_RATIO < (len(translated_buffer) / source_buffer_length):
                logger.debug('Returning buffer')
                return translated_buffer

    @abstractmethod
    def _get_result(self):
        pass


class AgentException(Exception):
    pass

class TEMPORARY_BAN_EXCEPTION(AgentException):
    def __init__(self):
        super().__init__('The server has temporarily banned this ip.')


class TIMEOUT_EXCEPTION(AgentException):
    def __init__(self):
        super().__init__(f"Waited for translation for {MAX_WAIT_FOR_TRANSLATION} seconds. Giving up.")


class UNKNOWN_EXCEPTION(AgentException):
    def __init__(self):
        super().__init__('The request failed for unknown reasons.')


class EXCEPTION_INSERTING_TEXT(AgentException):
    def __init__(self, buffer, original_exception):
        super().__init__(f'Exception {original_exception} inserting {buffer}')

class GoogleTranslateAgent(SeleniumAgentABC):
    language_names = {
        'dk': 'da',
    }

    def __init__(self, source_language, target_language):
        super().__init__(source_language, target_language)
        self.cookies_clicked = False
        if self.source_language in GoogleTranslateAgent.language_names:
            self.source_language = GoogleTranslateAgent.language_names[self.source_language]
        if self.target_language in GoogleTranslateAgent.language_names:
            self.target_language = GoogleTranslateAgent.language_names[self.target_language]


    def _url(self):
        return f"https://translate.google.com/#view=home&op=translate&sl={self.source_language}&tl={self.target_language}"

    def _insert_buffer(self, buffer):
        self.__click_cookies_modal()
        textarea = self.driver.find_element_by_css_selector('textarea')
        textarea.click()
        self.driver.execute_script(f'''
        const textarea = document.querySelector('textarea')
        textarea.click()
        textarea.value = `{buffer}`
        ''')
        return textarea

    def __click_cookies_modal(self):
        # time.sleep(1)
        self.driver.execute_script("document.querySelector('.gb_7').style.display = 'none';")

    def _get_result(self):
        result = -1
        for selector in (
                f'span[lang="{self.target_language}"]',
                'div[data-language]'
        ):
            try:
                result = self.driver.find_element_by_css_selector(selector)
                break
            except:
                continue
        if result == -1:
            raise AgentException('Translation could not be retrieved using any of the CSS selectors. Maybe the UI has changed?')
        return result.get_attribute("innerText")

class DeeplAgent(SeleniumAgentABC):

    def __init__(self, source_language, target_language):
        super().__init__(source_language, target_language)
        self.target_language = to_deepl_language(target_language)
        logger.debug(f'Target language is {self.target_language}; source language is {self.source_language}')

    def _url(self):
        return "http://www.deepl.com"

    def _insert_buffer(self, buffer):
        logger.debug('Will insert buffer')
        textarea = self.driver.find_element_by_class_name("lmt__source_textarea")
        while True:
            try:
                time.sleep(1)
                textarea.send_keys('  ')
                time.sleep(2)
                textarea.send_keys('  \n')
                logger.debug('Clicked keys')
                break
            except Exception as e:
                logger.warning(e)
        escaped_buffer = buffer.replace('`', '').replace('$', "S").replace("\\", "\\\\")
        self.driver.execute_script(f'''
        var cookiesButton = document.querySelector('button.dl_cookieBanner--buttonAll');
        if (cookiesButton) cookiesButton.click();
        var source_textarea = document.getElementsByClassName("lmt__source_textarea")[0];
        source_textarea.value = `{escaped_buffer}`
        source_textarea.dispatchEvent(new Event('change'))
        document.querySelector('button[dl-test="translator-source-lang-btn"]').click();
        document.querySelector('div[dl-test="translator-source-lang-list"]>button[dl-test="translator-lang-option-{self.source_language.lower()}"]').click();
        document.querySelector('button[dl-test="translator-target-lang-btn"]').click();
        document.querySelector('div[dl-test="translator-target-lang-list"]>button[dl-test="translator-lang-option-{self.target_language}"]').click();
        ''')
        return textarea

    def _get_result(self):
        logger.debug('Getting result')
        if self.__check_ip_blocked():
            raise TEMPORARY_BAN_EXCEPTION()

        progress_popup = self.driver.find_element_by_class_name('lmt__progress_popup')
        target_textarea = self.driver.find_element_by_class_name('lmt__target_textarea')
        if progress_popup.value_of_css_property('display') != 'none':
            logger.debug('Progress popup is active')
            return ""
        logger.debug('Will return buffer')
        logger.debug(target_textarea.get_attribute('value'))
        return target_textarea.get_attribute('value')

    def __check_ip_blocked(self):
        try:
            self.driver.find_element_by_class_name("lmt__notification__blocked")
            return True
        except:
            return False
