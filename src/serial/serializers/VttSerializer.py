from copy import copy

import webvtt

from util import convert_to_utf8

from .SerializerABC import SerializerABC
from serial.util import convert_to_key, format_caption

class VttSerializer(SerializerABC):
    def __init__(self, filename):
        fix_standalone_cues(filename)
        convert_to_utf8(filename)
        self.source = webvtt.read(filename)
        self.chunks_dictionary = {}

        for caption in self.source.captions:
            self.chunks_dictionary[convert_to_key(caption.text)] = ''

    def get_dictionary(self):
        return self.chunks_dictionary
    
    def set_dictionary(self, new_dictionary):
        self.chunks_dictionary = new_dictionary

    def save_to_file(self, output_filename):
        translation = copy(self.source)
        for caption in translation:
            print(caption)
            new_text = self.chunks_dictionary[convert_to_key(caption.text)]
            print(new_text)
            new_text_formatted = format_caption(new_text)
            caption.text = new_text_formatted
        print('finished')
        translation.save(output_filename)

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
