from copy import copy, deepcopy
from os.path import splitext

import webvtt

from util import convert_to_utf8

from .SerializerABC import SerializerABC
from serial.util import convert_to_key, format_caption

class VttSerializer(SerializerABC):

    def __init__(self, filename, source_language, target_language):
        super().__init__(filename, source_language, target_language)
        fix_standalone_cues(filename)
        convert_to_utf8(filename)

        self.source_language = source_language
        self.target_language = target_language
        self.source = webvtt.read(filename)
        self.translation_dictionary = {}
        self.lemmas_dictionary = {}

        for caption in self.source.captions:
            key = convert_to_key(caption.text)
            self.translation_dictionary[key] = ''
            self.lemmas_dictionary[key] = ''

    def get_translation_dictionary(self):
        return self.translation_dictionary

    def set_translation_dictionary(self, new_dictionary):
        self.translation_dictionary = new_dictionary

    def get_lemmas_dictionary(self):
        return self.lemmas_dictionary

    def set_lemmas_dictionary(self, new_dictionary):
        self.lemmas_dictionary = new_dictionary

    def save_to_file(self, output_filename):
        print('Saving')
        translation = self.__translate_source(self.translation_dictionary)
        lemmas = self.__translate_source(self.lemmas_dictionary, format_captions=False)
        translation.save(output_filename)
        lemmas_filename = splitext(output_filename)[0] + '.lemmas.' + splitext(output_filename)[1]
        lemmas.save(lemmas_filename)

    def __translate_source(self, dictionary, format_captions = True):
        translation = deepcopy(self.source)
        for caption in translation:
            key = convert_to_key(caption.text)
            new_text = dictionary[key] if key in dictionary else ""
            if key not in dictionary:
                print(f"NOT FOUND: {key}")
            if type(new_text) == dict:
                new_text = ','.join(new_text.values())
            if format_captions:
                new_text = format_caption(new_text)
            caption.text = new_text
        return translation


def fix_standalone_cues(filename):
    lines = []
    with open(filename, 'r') as file:
        previous_line_was_cue = False
        for line in file.readlines():
            if previous_line_was_cue and line == "\n":
                continue
            else:
                previous_line_was_cue = False
            if '-->' in line:
                previous_line_was_cue = True
            lines += [line,]

    clean_vtt = ''.join(lines)

    with open(filename, 'w') as file:
        file.write(clean_vtt)
