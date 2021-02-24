import os
import pickle
from shutil import which

from selenium import webdriver  
from selenium.webdriver.chrome.options import Options

from config import HEADLESS_MODE, SELENIUM_TIMEOUT, TRANSLATION_DICTIONARY_FILENAME


def make_headless_selenium_driver(headless_mode=HEADLESS_MODE, timeout=SELENIUM_TIMEOUT):
    binary_path = which('chromedriver')
    options = Options()
    if headless_mode:
        options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=binary_path,
                              chrome_options=options)
    driver.implicitly_wait(timeout)
    return driver

def pretty_print(translations):
    for source, translation in translations.items():
        print(f"{source}\n{translation}\n")


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


languages = ['en', 'es', 'de', 'zh', 'fr', 'da']
languages_map = {
    'deu': 'de',
    'esp': 'es',
    'eng': 'en',
    'en-us': 'en',
    'en-US': 'en'
}

deepl_languages = {
    'en': 'en-US'
}

to_deepl_language = lambda lang: deepl_languages[lang] if lang in deepl_languages else f"{lang.lower()}-{lang.upper()}"

is_recognized_language = lambda language: language in languages or language in languages_map


def infer_language(language):
    language = language.lower()
    if language in languages:
        return language
    if language in languages_map:
        return languages_map[language]
    raise Exception(f"Could not infer language from '{language}'")

