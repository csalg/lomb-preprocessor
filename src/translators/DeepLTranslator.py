import os  
from shutil import which
from random import randint
from dataclasses import dataclass
from time import sleep
from datetime import datetime, timedelta
import pickle

from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 

from .TranslatorABC import TranslatorABC

PHRASE_SEPARATOR = "\n-&----&-\n"
ID_SEPARATOR = "\n"
MIN_WAIT_FOR_TRANSLATION = 5
MAX_WAIT_FOR_TRANSLATION = 10
MAX_CHARACTERS_PER_BUFFER = 3200
MAX_NUMBER_OF_REQUESTS_WITH_SAME_DRIVER = 30
WAIT_BETWEEN_DRIVER_CHANGE = 120
MAX_NEW_SESSIONS_BEFORE_GIVING_UP = 5
SELENIUM_TIMEOUT = MAX_WAIT_FOR_TRANSLATION
URL = "http://www.deepl.com"
HEADLESS = False
MINIMUM_ACCEPTABLE_TRANSLATION_RATIO = 0.2
WAIT_FOR_IP_UNBLOCK = 60*60


def make_headless_selenium_driver():
    binary_path = which('chromedriver')
    options     = Options()
    if HEADLESS:
        options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=binary_path,
                            chrome_options=options)
    driver.implicitly_wait(SELENIUM_TIMEOUT)
    return driver



class DeepLTranslator(TranslatorABC):
    def __init__(self, source_language, target_language):
        self.driver = make_headless_selenium_driver()
        self.source_language = source_language
        self.target_language = target_language
    

    def translate(self,translation_dictionary):

        self.driver.get(URL)
        
        def make_intermediate_dictionary():
            intermediate_dictionary = {}
            i = randint(2400, 9999)
            for key in translation_dictionary.keys():
                intermediate_dictionary[i] = key
                i += 1
            return intermediate_dictionary
        
        def restart_driver():
            self.driver.close()
            self.driver = make_headless_selenium_driver()
            self.driver.get(URL)
            print("Driver was restarted.")

        def restore_or_use_translation_dictionary(translation_dictionary):
            if os.path.exists('translation_dictionary.pkl'):
                with open('translation_dictionary.pkl', 'rb') as file:
                    translation_dictionary = pickle.load(file)
                return translation_dictionary
            else:
                return translation_dictionary

        translation_dictionary = restore_or_use_translation_dictionary(translation_dictionary)
        intermediate_dictionary = make_intermediate_dictionary()

        def persist_translation_dictionary():
            nonlocal translation_dictionary
            with open('translation_dictionary.pkl', 'wb') as file:
                pickle.dump(translation_dictionary, file)
        
        def delete_translation_dictionary_from_disk():
            nonlocal intermediate_dictionary
            if os.path.exists('translation_dictionary.pkl'):
                os.remove('translation_dictionary.pkl')

        number_of_requests_with_same_driver = 0

        def dispatch_translation(buffer):
            nonlocal number_of_requests_with_same_driver

            source_textarea = self.driver.find_elements_by_class_name("lmt__source_textarea")[0]
            sleep(1)
            source_textarea.send_keys('  ')
            sleep(2)
            source_textarea.send_keys('  \n')

            self.driver.execute_script(f'''
            document.querySelector('button[dl-lang="{self.source_language.upper()}"]').click();
            document.querySelector('div[dl-test="translator-target-lang-list"]>button[dl-lang="{self.target_language.upper()}"]').click();
            var source_textarea = document.getElementsByClassName("lmt__source_textarea")[0];
            source_textarea.value = `{buffer}`
            source_textarea.dispatchEvent(new Event('change'))
            document.querySelector('button[dl-lang="{self.source_language.upper()}"]').click();
            document.querySelector('div[dl-test="translator-target-lang-list"]>button[dl-lang="{self.target_language.upper()}"]').click();
            ''')

            translated_buffer = ""
            while len(translated_buffer)/len(buffer) < MINIMUM_ACCEPTABLE_TRANSLATION_RATIO:
                source_textarea.send_keys('  ')
                block_until_translation_received()
                target_textarea = self.driver.find_elements_by_class_name("lmt__target_textarea")[0] 
                translated_buffer = str(target_textarea.get_attribute('value'))
                if translated_buffer == "":
                    raise Exception("Translation failed!")



            number_of_requests_with_same_driver += 1
            return translated_buffer
        

        def block_on_ip_blocked():
            time_to_resume = datetime.now()+timedelta(seconds=WAIT_FOR_IP_UNBLOCK)
            time_to_resume_str = time_to_resume.strftime('%H:%M:%S')
            print(f"Blocking until {time_to_resume_str} minutes because ip was blocked.")
            sleep(WAIT_FOR_IP_UNBLOCK)
        

        def check_ip_blocked():
            try:
                self.driver.find_element_by_class_name("lmt__notification__blocked")
                return True
            except:
                return False


        def block_until_translation_received():
            start_time = datetime.now()
            max_time = start_time + timedelta(seconds=MAX_WAIT_FOR_TRANSLATION)
            min_time = start_time + timedelta(seconds=MIN_WAIT_FOR_TRANSLATION)
            while True:
                if datetime.now() > max_time:
                    return
                if datetime.now() < min_time:
                    continue
                elif check_ip_blocked():
                    block_on_ip_blocked()
                    raise Exception("IP was blocked!")
                else:
                    progress_popup = self.driver.find_elements_by_class_name('lmt__progress_popup')[0]
                    target_textarea = self.driver.find_elements_by_class_name('lmt__target_textarea')[0]
                    if progress_popup.value_of_css_property('display') == 'none' and \
                        target_textarea.get_attribute('value'):
                        return
                sleep(1)


        def encode_for_deepl(id, phrase):
            return f'{id}{ID_SEPARATOR}{phrase}{PHRASE_SEPARATOR}'
        

        def decode_from_deepl(buffer):
            raw_phrases = buffer.split(PHRASE_SEPARATOR)
            print(raw_phrases)
            return map(lambda raw_phrase : IdAndTranslation(ID_SEPARATOR, raw_phrase), raw_phrases)
        

        def update_translation_dictionary(buffer):
            print('buffer: ', buffer)
            save_buffer(buffer)
            translated_phrases = decode_from_deepl(buffer)
            for translated_phrase in translated_phrases:
                try:
                    print(translated_phrase.id, translated_phrase.text)
                    key = intermediate_dictionary[translated_phrase.id]
                    print(key)
                    translation_dictionary[key] = translated_phrase.text
                    print(translated_phrase.text)
                except:
                    pass
            persist_translation_dictionary()
        
        def save_buffer(buffer):
            with open('deepl.log', 'a') as file:
                file.write(buffer)



        def try_to_dispatch_translation(buffer):
            nonlocal number_of_requests_with_same_driver
            attempts = 0
            if number_of_requests_with_same_driver >= MAX_NUMBER_OF_REQUESTS_WITH_SAME_DRIVER:
                print('Restarting driver because too many requests with same driver.')
                sleep(WAIT_BETWEEN_DRIVER_CHANGE)
                restart_driver()
                number_of_requests_with_same_driver = 0
            while attempts < MAX_NEW_SESSIONS_BEFORE_GIVING_UP:
                try:
                    translation = dispatch_translation(buffer)
                    return translation
                except Exception as e:
                    print(e)
                    restart_driver()
                    attempts += 1
            raise Exception(f"Translation failed after {MAX_NEW_SESSIONS_BEFORE_GIVING_UP} attempts!")

        will_translate_buffer = ""

        for id, phrase in intermediate_dictionary.items():
            if translation_dictionary[phrase]:
                continue
            if len(will_translate_buffer) + len(phrase) > MAX_CHARACTERS_PER_BUFFER:
                translated_buffer = try_to_dispatch_translation(will_translate_buffer)
                update_translation_dictionary(translated_buffer)
                will_translate_buffer = ""
            will_translate_buffer += encode_for_deepl(id, phrase)
        if will_translate_buffer:
            translated_buffer = try_to_dispatch_translation(will_translate_buffer)
            update_translation_dictionary(translated_buffer)
        delete_translation_dictionary_from_disk()
        print("Finished translation")
        return translation_dictionary

class IdAndTranslation():
    def __init__(self,ID_SEPARATOR, raw_phrase):
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
