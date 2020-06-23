import os
import json
from os.path import splitext

from celery import Celery

# from jobs.TranslationJobABC import TranslationJob
from serial import SerializerSimpleFactory
from translators.DeepLTranslator import DeepLTranslator
from translators.util import infer_language
from taggers.Tagger import GermanTagger
from util import parse_title_source_language_and_extension_from_filename


class LocalTranslationJob():
    def __init__(self, source_language, target_language, input_filename, input_json):
        self.source_language        = self._deduce_source_language(input_filename, source_language)
        self.target_language        = self._deduce_target_language(target_language)
        self.title, self.extension  = self._split_filename_into_title_and_extension(input_filename)

        serializer_constructor = SerializerSimpleFactory.create(self.extension)
        self.serializer = serializer_constructor(input_filename, self.source_language, self.target_language)
        self.tagger = GermanTagger()
        self.translator = DeepLTranslator(self.source_language, self.target_language)

    def run(self):
        print(f'Executing: {self.output_filename()}')

        translation_dictionary = self.serializer.get_translation_dictionary()
        if self.source_language != self.target_language:
            translation_dictionary = self.translator.translate(translation_dictionary)

        lemmas_dictionary = self.serializer.get_lemmas_dictionary()
        lemmas_dictionary = self.tagger.tag(lemmas_dictionary)

        self.serializer.set_translation_dictionary(translation_dictionary)
        self.serializer.set_lemmas_dictionary(lemmas_dictionary)
        print("Translation finished")
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


# class RemoteTranslationJob(TranslationJob):
    # def __init__(self,*args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    # def run(self):
    #     pass
    #

def run_local_translation_job_from_filename(source_language, target_language, input_filename, input_json=None):
    job = LocalTranslationJob(source_language, target_language, input_filename, input_json)
    job.run()

# def run_local_translation_job_from_filename(input_filename, given_source_language, target_language, input_json=None):
#
#     source_language = deduce_source_language(input_filename, given_source_language)
#     target_language = deduce_target_language(target_language)
#     title, extension = split_filename_into_title_and_extension(input_filename)
#     output_filename = make_output_filename(title, extension)
#
#     if not is_recognized_language(target_language):
#         raise Exception(f"Target language '{target_language}' is not recognized.")
#
#     if given_source_language:
#         source_language = given_source_language
#         title, extension = os.path.splitext(input_filename)
#         extension = extension[1:]
#     else:
#         title, source_language, extension = parse_title_source_language_and_extension_from_filename(input_filename)
#
#     inferred_source_language = infer_language(source_language)
#
#     output_filename = f'{title}.{target_language}.{extension}'
#     print(output_filename)
#
#     if not is_recognized_extension(extension):
#         raise Exception(f"Extension '{extension}' is not recognized.")
#
#     if not is_recognized_language(inferred_source_language):
#         raise Exception(f"Source language '{source_language}' is not recognized.")
#
#     if extension != 'epub':
#         convert_to_utf8(input_filename)
#         get_rid_of_empty_lines_after_time_in_vtt(input_filename)
#
#     if requires_conversion(extension):
#         print('converting')
#         new_filename = convert(input_filename)
#         return run_local_translation_job_from_filename(new_filename, given_source_language, target_language)
#
#     if os.path.exists(output_filename) or os.path.exists(output_filename+'.json'):
#         raise Exception(f"Translated file '{output_filename}' already exists")
#
#     serializer_constructor = serializer_from_extension(extension)
#     translator_constructor = DeepLTranslator
#
#     serializer = serializer_constructor(input_filename)
#     if input_json:
#         previous_translation_dictionary = get_dictionary_from_json(input_json)
#         serializer.set_dictionary(previous_translation_dictionary)
#     translator = translator_constructor(inferred_source_language, target_language)
#
#     job = LocalTranslationJob(output_filename, serializer, translator)
#     job.run()
#
#
# def run_package_translation_job(given_source_language, target_language, filenames, input_json=None):
#
#     if not is_recognized_language(target_language):
#         raise Exception(f"Target language '{target_language}' is not recognized.")
#
#     if not given_source_language:
#         raise Exception('Cannot infer source language for packaged texts. Please provide a source language.')
#
#     metadata = get_metadata(filenames[0])
#     output_filename = f'{metadata["title"]}.{target_language}'
#     print(output_filename)
#
#     inferred_source_language = infer_language(given_source_language)
#     if not is_recognized_language(inferred_source_language):
#         raise Exception(f"Source language '{inferred_source_language}' is not recognized.")
#
#     for filename in filenames:
#         convert_to_utf8(filename)
#
#     if os.path.exists(output_filename) or os.path.exists(output_filename+'.json'):
#         raise Exception(f"Translated file '{output_filename}' already exists")
#
#     metadata['source_language'] = inferred_source_language
#     metadata['support_language'] = target_language
#     serializer = TextPackageSerializer(metadata, filenames)
#     translator_constructor = DeepLTranslator
#
#     if input_json:
#         previous_translation_dictionary = get_dictionary_from_json(input_json)
#         serializer.set_dictionary(previous_translation_dictionary)
#     translator = translator_constructor(inferred_source_language, target_language)
#
#     job = LocalTranslationJob(output_filename, serializer, translator)
#     job.run()
#
#
# @celery.task
# def run_local_translation_job_from_filename_celery_task(*args, **kwargs):
#     """     try:
#         run_local_translation_job_from_filename(*args, **kwargs)
#     except Exception as e:
#         print(e) """
#     run_local_translation_job_from_filename(*args, **kwargs)
#
#
