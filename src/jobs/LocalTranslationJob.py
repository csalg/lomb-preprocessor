import os
from os.path import splitext

from termcolor import colored

import serial
from util import LombPreprocessorException, infer_language
from logging_ import logger
from taggers import create_tagger
from translators.selenium_translators import GoogleTranslator, DeepLTranslator
from util import parse_title_source_language_and_extension_from_filename


class LocalTranslationJob():
    def __init__(self, source_language, target_language, input_filename, input_json):
        self.source_language        = self._deduce_source_language(input_filename, source_language)
        self.target_language        = self._deduce_target_language(target_language)
        self.title, self.extension  = self._split_filename_into_title_and_extension(input_filename)
        if os.path.isfile(self.output_filename()):
            raise FileExistsException(f'{self.output_filename()} found in directory. Skipping')

        self.serializer = serial.create_serializer(input_filename, self.source_language, self.target_language)
        self.tagger = create_tagger(self.source_language)
        if self.source_language in ['dk', 'da']:
            self.translator = GoogleTranslator('da', self.target_language)
        else:
            self.translator = DeepLTranslator(self.source_language, self.target_language)

    def run(self):
        logger.info(f'{colored(self.title + "." + self.extension, "yellow")} will be translated from {colored(self.source_language, "red")} to {colored(self.target_language, "red")}')

        translation_dictionary = self.serializer.get_translation_dictionary()
        if self.source_language != self.target_language:
            translation_dictionary = self.translator.translate(translation_dictionary)
        self.serializer.set_translation_dictionary(translation_dictionary)

        lemmas_dictionary = self.serializer.get_lemmas_dictionary()
        lemmas_dictionary = self.tagger.tag(lemmas_dictionary)

        self.serializer.set_lemmas_dictionary(lemmas_dictionary)
        logger.info(colored("Translation finished", 'green'))
        self.serializer.save_to_file(self.output_filename())

    def _deduce_source_language(self, input_filename, given_source_language):
        if given_source_language:
            source_language = given_source_language
        else:
            _, source_language, _ = parse_title_source_language_and_extension_from_filename(input_filename)

        return infer_language(source_language)

    def _deduce_target_language(self, target_language):
        return infer_language(target_language)

    def output_filename(self):
        return f'{self.title}.{self.target_language}.{self.extension}'

    def _split_filename_into_title_and_extension(self, input_filename):
        title, ext = splitext(input_filename)
        return title, ext[1:]


class FileExistsException(LombPreprocessorException):
    pass

def run_local_translation_job_from_filename(source_language, target_language, input_filename, input_json=None):
    try:
        job = LocalTranslationJob(source_language, target_language, input_filename, input_json)
        job.run()
    except LombPreprocessorException as e:
        logger.warning(colored(e, 'blue'))

